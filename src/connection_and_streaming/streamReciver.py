import time
import logging
import json
from tkinter.constants import NW

import keyboard
from threading import Thread
import base64
import numpy as np
import cv2
from PIL import Image, ImageTk
from mqtt_client import MqttClient


FPS = 30
CHANNELS = 1
RATE = 44100

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883
MQTT_TOPIC_RECIVER = "ttm4115/team_1/project/reciver"


class StreamVideoReciver():
    def on_connect(self, client, userdata, flagSs, rc):
        self._logger.debug("MQTT connected to {}".format(client))

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
                self.mqtt_client.subscribe("ttm4115/team_1/project/camera"+self.recivefrom[-1])
                self.active =True
            elif data["command"] == "streamstop" and data["reciver"]== self.name:
                self.active =False  
                self.mqtt_client.unsubscribe("ttm4115/team_1/project/camera"+self.recivefrom[-1])
                self.recivefrom =None
                self.framesaudio =[]
                cv2.destroyAllWindows()
        if self.recivefrom != None:
            if msg.topic == "ttm4115/team_1/project/camera"+self.recivefrom[-1] :#and not_sleep
                data =self.load_json(msg)
                if data["command"] == "streamvideo" and data["reciver"]== self.name and self.active ==True:
                    framevideo=self.bts_to_frame(data["answer"])
                    self.frame = frame_video
                    self.start_stream()
                    # cv2.imshow("webcam", framevideo)
                    # cv2.waitKey(20)

    def bts_to_frame(self, b64_string):
        base64_bytes = b64_string.encode("utf-8")
        buff = np.frombuffer(base64.b64decode(base64_bytes), np.uint8)
        img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
        return img

    def __init__(self, canvas, height, width):
        self.number = 1
        self.name = "office" + str(self.number) + "reciver"
        self.active = False
        self.framesaudio = []
        self.recivefrom = None

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print("logging under name {}.".format(__name__))
        self._logger.info("Starting Component")

        # create a new MQTT client
        self._logger.debug("Connecting to MQTT broker {} at port {}".format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = MqttClient("StreamReciver" + self.name)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(MQTT_TOPIC_RECIVER)
        t1 = Thread(target=self.mqtt_client.loop_start())
        t1.start()

        # t2 = Thread(target=self.start())
        # t2.start()

        # for tkinter
        self.canvas = canvas
        self.height = height
        self.width = width
        self.frame = None
        self.started_stream = False

    def start(self):
        while True:
            time.sleep(0.001)
            try:
                pass
                # if keyboard.is_pressed("Escape"):
                #   break
            except:
                pass

    def start_stream(self):
        if not self.started_stream:
            self.started_stream = True
            self.show_stream()

    def show_stream(self):
        frame = cv2.resize(self.frame, (self.height, self.width))
        self.image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # to RGB
        self.image = Image.fromarray(self.image)  # to PIL format
        self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format
        # Update image
        self.canvas.create_image(0, 0, anchor=NW, image=self.image)
        self.canvas.after(10, self.show_stream)


if __name__ == "__main__":
    debug_level = logging.DEBUG
    logger = logging.getLogger(__name__)
    logger.setLevel(debug_level)
    ch = logging.StreamHandler()
    ch.setLevel(debug_level)
    formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    t = StreamVideoReciver()
