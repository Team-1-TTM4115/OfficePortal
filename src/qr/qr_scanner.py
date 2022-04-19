import tkinter
from tkinter.ttk import Label

import PIL
import cv2
from PIL import Image, ImageTk
from pyzbar import pyzbar
from src.mqtt_client import MqttClient

TOPIC_CONNECT = 'ttm4115/team_1/project/connect'


class QrReader:
    def __init__(self, frame):
        self.__mqtt_client = MqttClient("QrReader")
        self.capture = None
        self.gui_window = frame

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
        self.capture = camera

        ret, frame = camera.read()
        frame = self.__read_barcodes(frame)
        cv2.imshow('Barcode/QR code reader', frame)
        # TODO: FIgure out what it does.
        # if cv2.waitKey(1) & 0xFF == 27:

        canvas = tkinter.Canvas(self.gui_window, width=200, height=200)
        canvas.pack()
        photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        # Add a PhotoImage to the Canvas
        canvas.create_image(0, 0, image=photo, anchor=tkinter.NW)
        self.gui_window.after(10, self.capture_video)

    def stop_capture(self):
        self.capture.release()
        cv2.destroyAllWindows()
