import time
import logging
import json

from threading import Thread
import pyaudio
from mqtt_client import MqttClient
import stmpy

FPS = 30
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883
MQTT_TOPIC_RECIVER = "ttm4115/team_1/project/reciver"


class StreamAudioLogic:
    def __init__(self, name, component):
        self._logger = logging.getLogger(__name__)
        self.name = name
        self.id = name
        self.component = component

        t0 = {
            "source": "initial",
            "target": "off",
        }

        t1 = {
            "trigger": "turn_audio_reciver_on",
            "source": "off",
            "target": "on",
            "effect": "start_audio",
        }
        t2 = {
            "trigger": "turn_audio_reciver_off",
            "source": "on",
            "target": "off",
            "effect": "stopp_audio",
        }

        on = {"name": "on",
              "play_frame": "play_audio(*)", }

        self.stm = stmpy.Machine(name=name,
                                 transitions=[t0, t1, t2],
                                 obj=self, states=[on])

    def play_audio(self, frame):
        self.component.play_audio(frame)

    def stopp_audio(self):
        self.component.stop_audio()

    def start_audio(self):
        self.component.start_audio()


class StreamAudioReciver:
    def __init__(self, name):
        self.number = name[-1]
        self.name = "office" + str(self.number) + "reciver"
        self.active = False
        self.firstframeaudio = 0
        self.framesaudio = []
        self.recivefrom = None
        self.frame = None

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print("logging under name {}.".format(__name__))
        self._logger.info("Starting Component")

        # create a new MQTT client
        self._logger.debug("Connecting to MQTT broker {} at port {}".format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = MqttClient("StreamRecivera" + self.name)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(MQTT_TOPIC_RECIVER)
        t1 = Thread(target=self.mqtt_client.loop_start())
        t1.start()

        self.stm_driver = None
        controller = StreamAudioLogic('streamaudio', self)
        self.stm = controller.stm

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when connected to MQTT
        """
        self._logger.debug("MQTT connected to {}".format(client))

    def play_audio(self, frame):
        """
        Write frame to audio stream
        """
        self.stream.write(frame, num_frames=2048)

    def start_audio(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True, )

    def stop_audio(self):
        """
        Stop and terminate audio stream
        :return:
        """
        self.stream.close()
        self.p.terminate()

    def load_json(self, msg):
        """
        Deserialize JSON string
        """
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        return data

    def on_message(self, client, userdata, msg):
        """
        Callback when recieving a message on subscribed topic through MQTT
        """
        if msg.topic == 'ttm4115/team_1/project/reciver':
            data = self.load_json(msg)
            if data["command"] == "streamstart" and data["reciver"] == self.name:
                self.recivefrom = data["answer"]
                self.mqtt_client.subscribe("ttm4115/team_1/project/audio" + self.recivefrom[-1])
                self.stm_driver.send("turn_audio_reciver_on", "streamaudio")
            elif data["command"] == "streamstop" and data["reciver"] == self.name:
                self.mqtt_client.unsubscribe("ttm4115/team_1/project/audio" + self.recivefrom[-1])
                self.recivefrom = None
                self.stm_driver.send("turn_audio_reciver_off", "streamaudio")
        if self.recivefrom is not None:
            if msg.topic == "ttm4115/team_1/project/audio" + self.recivefrom[-1]:
                data = self.load_json(msg)
                if data["command"] == "streamaudio" and data["reciver"] == self.name:
                    self.stm_driver.send("play_frame", "streamaudio",
                                         kwargs={"frame": data["answer"].encode("ISO-8859-1")})

    def start(self):
        while True:
            time.sleep(0.001)
