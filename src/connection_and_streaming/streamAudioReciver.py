import time
import logging
import json

from threading import Thread
import base64
import numpy as np
import cv2
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
        "play_frame": "play_audio(*)",}

        self.stm = stmpy.Machine(name=name, 
        transitions=[t0,t1,t2],
        obj=self, states=[on])


    def play_audio(self,frame):
        self.component.play_audio(frame)

    def stopp_audio(self):
        self.component.stopp_audio()

    def start_audio(self):
        self.component.start_audio()


class StreamAudioReciver():
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug("MQTT connected to {}".format(client))

    def callback(self, in_data, frame_count, time_info, status):
        data = None
        if (len(self.framesaudio) != 0):
            data = self.framesaudio.pop(0)
        else:
            while len(self.framesaudio) == 0:
                time.sleep(0.01)
                if (len(self.framesaudio) != 0):
                    data = self.framesaudio.pop(0)
                    break
        return (data, pyaudio.paContinue)
    """
    def play_audio(self):
        p = pyaudio.PyAudio() 
        self.stream = p.open(format=FORMAT,
                             channels=CHANNELS,
                             rate=RATE,
                             output=True,
                             stream_callback=self.callback)
        self.stream.start_stream()
        while self.stream.is_active():
            time.sleep(0.1)
        self.stream.close()
        p.terminate()
    """
    def play_audio(self,frame):
        self.stream.write(frame,num_frames=2048) #1024
        

    def start_audio(self):
        self.p = pyaudio.PyAudio() 
        self.stream = self.p.open(format=FORMAT,
                             channels=CHANNELS,
                             rate=RATE,
                             output=True,)

    def stopp_audio(self):
        self.stream.close
        self.p.terminate()

    def load_json(self, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        return data

    def on_message(self, client, userdata, msg):
        if msg.topic == 'ttm4115/team_1/project/reciver':
            data =self.load_json(msg)
            if data["command"] == "streamstart" and data["reciver"]== self.name:
                self.recivefrom =data["answer"]
                self.mqtt_client.subscribe("ttm4115/team_1/project/audio"+self.recivefrom[-1])
                self.stm_driver.send("turn_audio_reciver_on", "streamaudio")
                #self.active =True
            elif data["command"] == "streamstop" and data["reciver"]== self.name:
                #self.active =False  
                self.mqtt_client.unsubscribe("ttm4115/team_1/project/audio"+self.recivefrom[-1])
                self.recivefrom =None
                self.stm_driver.send("turn_audio_reciver_off", "streamaudio")
                #self.stream.stop_stream()
                #self.framesaudio = []
                #self.firstframeaudio = 0
                #cv2.destroyAllWindows()
        if self.recivefrom != None:
            if msg.topic == "ttm4115/team_1/project/audio" + self.recivefrom[-1]:
                data =self.load_json(msg)
                if data["command"] == "streamaudio" and data["reciver"]== self.name:
                    self.stm_driver.send("play_frame", "streamaudio", kwargs={"frame": data["answer"].encode("ISO-8859-1")})
                    #if self.firstframeaudio == 0:
                        #self.firstframeaudio = int(data["time"])
                        #y=Thread(target=self.play_audio)#
                        #y.start()
                    #else:
                        #self.framesaudio.append(data["answer"].encode("ISO-8859-1"))


    #def __init__(self):
    def initialize_stm(self,name):
        self.number = 7#name[-1]
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
        t1 = Thread(target=self.mqtt_client.loop_start())  # Thread
        t1.start()

        #t2 = Thread(target=self.start())
        #t2.start()

        self.stm_driver =None
        controller= StreamAudioLogic('streamaudio',self)
        self.stm= controller.stm

        #self.stm_driver = stmpy.Driver()
        #self.stm_driver.add_machine(self.stm)
        #self.stm_driver.start()

    def start(self):
        while True:
            time.sleep(0.001)
            try:
                pass
                # if keyboard.is_pressed("Escape"):
                #    break
            except:
                pass

if __name__ =="__main__":

    debug_level = logging.DEBUG
    logger = logging.getLogger(__name__)
    logger.setLevel(debug_level)
    ch = logging.StreamHandler()
    ch.setLevel(debug_level)
    formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    t = StreamAudioReciver()
