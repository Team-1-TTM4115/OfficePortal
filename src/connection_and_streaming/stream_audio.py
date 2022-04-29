from mqtt_client import MqttClient
import logging
import json

import time
import pyaudio
from threading import Thread

CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883
MQTT_TOPIC_AUDIO = "ttm4115/team_1/project/audio"
MQTT_TOPIC_CAMERA = "ttm4115/team_1/project/camera"


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
            "trigger": "turn_audio_on",
            "source": "off",
            "target": "on",
            "effect": "start_timer('adiuo_timer', 45); audio_on",
        }
        t2 = {
            "trigger": "turn_audio_off",
            "source": "on",
            "target": "off",
        }

        on = {"name": "on",
              "audio_timer": "start_timer('sensor_timer', 45); check_movement", }

    def audio_on(self):
        self.component.audio_on()


class StreamAudio():
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when connecting to MQTT
        """
        self._logger.debug("MQTT connected to {}".format(client))

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
        Callback when recieving message to subscribed topic through MQTT
        """
        if msg.topic == "ttm4115/team_1/project/audio" + str(self.number):
            data = self.load_json(msg)
            if data["command"] == "streamstart" and data["reciver"] == self.name + "audio":
                self.active = True
                self.sendTo = data["answer"]
            elif data["command"] == "streamstop" and data["reciver"] == self.name + "audio":
                self.active = False

    def __init__(self):
        self.number = 8
        self.name = "office" + str(self.number)
        self.sendTo = None
        self.active = False
        self.on = True

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print("logging under name {}.".format(__name__))
        self._logger.info("Starting Component")

        # create a new MQTT client
        self._logger.debug("Connecting to MQTT broker {} at port {}".format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = MqttClient("StreamAudio" + str(self.number))
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe("ttm4115/team_1/project/audio" + str(self.number))
        thread = Thread(target=self.mqtt_client.loop_start())
        thread.start()

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        while True:
            while self.active:
                data = stream.read(CHUNK)
                audiostring = data.decode("ISO-8859-1")
                timestamp = str(int(time.time() * 1000))
                self.send_msg("streamaudio", "office" + str(self.number) + "audio", self.sendTo, timestamp, audiostring,
                              "ttm4115/team_1/project/audio" + str(self.number))
        self.mqtt_client.loop_stop()
        stream.stop_stream()
        stream.close()
        p.terminate()

    def audio_on(self):
        pass

    def send_msg(self, msg, sender, reciver, timestamp, answer, where):
        """
        Serialize into JSON string and publish to MQTT topic
        :param where: Topic to publish to
        """
        command = {"command": msg, "sender": sender, "reciver": reciver, "time": timestamp, "answer": answer}
        payload = json.dumps(command)
        self.mqtt_client.publish(where, payload)


if __name__ == "__main__":
    debug_level = logging.DEBUG
    logger = logging.getLogger(__name__)
    logger.setLevel(debug_level)
    ch = logging.StreamHandler()
    ch.setLevel(debug_level)
    formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    t = StreamAudio()
