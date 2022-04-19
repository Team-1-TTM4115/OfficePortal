import tkinter
from tkinter import NW

import cv2
from PIL import Image, ImageTk
from pyzbar import pyzbar

from src.mqtt_client import MqttClient

TOPIC_CONNECT = 'ttm4115/team_1/project/connect'


class QrReader:
    def __init__(self, frame, height, width):
        self.__mqtt_client = MqttClient("QrReader")
        self.cap = None
        self.gui_window = frame
        self.image = None
        self.canvas = None
        self.height = height
        self.width = width

    def __read_barcodes(self, frame):
        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            x, y, w, h = barcode.rect

            barcode_info = barcode.data.decode('utf-8')
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            self.__mqtt_client.publish(TOPIC_CONNECT, barcode_info)
            # TODO: Do something after scanning a code. Like trying to connect?
        return frame

    def capture_video(self):
        # TODO: Integrate into gui somehow
        camera = cv2.VideoCapture(0)
        self.cap = camera

        self.canvas = tkinter.Canvas(self.gui_window, bg='black', borderwidth=0)
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        self.update_qr_frame()

    def update_qr_frame(self):
        # Get the latest frame and convert image format
        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (self.height, self.width))
        frame = self.__read_barcodes(frame)
        self.image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # to RGB
        self.image = Image.fromarray(self.image)  # to PIL format
        self.image = ImageTk.PhotoImage(self.image)  # to ImageTk format

        # Update image
        self.canvas.create_image(0, 0, anchor=NW, image=self.image)
        self.canvas.after(10, self.update_qr_frame)

    def stop_capture(self):
        self.cap.release()
        cv2.destroyAllWindows()
