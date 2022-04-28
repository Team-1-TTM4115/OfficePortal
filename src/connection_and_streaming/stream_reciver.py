import time
import logging
import json
from tkinter.constants import NW
import tkinter as tk
import base64
import numpy as np
import cv2
from PIL import Image, ImageTk
from mqtt_client import MqttClient
from threading import Thread

FPS = 30
CHANNELS = 1
RATE = 44100

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883
MQTT_TOPIC_RECIVER = "ttm4115/team_1/project/reciver"


class StreamVideoReciver:
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
            data = self.load_json(msg)
            if data["command"] == "streamstart" and data["reciver"] == self.name:
                self.recivefrom = data["answer"]
                self.mqtt_client.subscribe("ttm4115/team_1/project/camera" + self.recivefrom[-1])
                self.active = True
            elif data["command"] == "streamstop" and data["reciver"] == self.name:
                self.active = False
                self.mqtt_client.unsubscribe("ttm4115/team_1/project/camera" + self.recivefrom[-1])
                self.recivefrom = None
                self.framesaudio = []
                cv2.destroyAllWindows()
        if self.recivefrom is not None:
            if msg.topic == "ttm4115/team_1/project/camera" + self.recivefrom[-1]:
                data = self.load_json(msg)
                if data["command"] == "streamvideo" and data["reciver"] == self.name and self.active == True:
                    framevideo = self.bts_to_frame(data["answer"])

                    self.frame = framevideo
                    self.start_stream()

    def bts_to_frame(self, b64_string):
        base64_bytes = b64_string.encode("utf-8")
        buff = np.frombuffer(base64.b64decode(base64_bytes), np.uint8)
        img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
        return img

    def set_canvas(self, canvas, height, width, gui_frame):
        self.canvas = canvas
        self.height = height
        self.width = width
        self.gui_frame = gui_frame

    def __init__(self, name):

        self.number = name[-1]
        self.name = "office" + str(self.number) + "reciver"
        self.active = False
        self.framesaudio = []
        self.recivefrom = None

        # get sthe logger object for the component
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
        self.frame = None
        self.started_stream = False
        self.canvas = None
        self.filter_frame = None
        self.height = None
        self.width = None
        self.showing = False

    def set_is_showing(self, is_showing):
        self.showing = is_showing

    def start(self):
        while True:
            time.sleep(0.001)

    def start_stream(self):
        if not self.started_stream:
            self.started_stream = True
            self.show_stream()

    def show_stream(self):
        frame = cv2.resize(self.frame, (self.width, self.height))
        self.image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # to RGB
        self.image = Image.fromarray(self.image)  # to PIL format
        self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

        # Update image
        if self.showing:
            self.create_filter_page(self.gui_frame)
        else:
            if self.filter_frame is not None:
                self.filter_frame.destroy()
                self.filter_frame = None
        self.canvas.create_image(0, 0, anchor=NW, image=self.image)
        self.canvas.after(10, self.show_stream)

    def create_filter_page(self, parent_frame: tk.Frame):
        filters = ['dog', 'glasses', 'easter', 'lofoten', 'vacation', ]
        if self.filter_frame is None:
            self.filter_frame = tk.Frame(parent_frame, bg='black')
            self.filter_frame.place(x=self.width / 2, y=self.height / 8, anchor=tk.CENTER)
            current = 'misc'

            for index in range(len(filters)):
                if current == filters[index]:
                    button1 = tk.Label(self.filter_frame, text=filters[index], bg='grey', fg='white',
                                       font=("Helvetica", 40),
                                       borderwidth=10, relief=tk.GROOVE, )
                    button1.grid(row=0, column=index, padx=10, pady=10)
                else:
                    button1 = tk.Label(self.filter_frame, text=filters[index], bg='grey', fg='white',
                                       font=("Helvetica", 40))
                    button1.grid(row=0, column=index, padx=10, pady=10)
