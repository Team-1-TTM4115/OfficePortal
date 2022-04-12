import cv2
from pyzbar import pyzbar
from src.mqtt_client.mqtt_client import MqttClient

TOPIC_CONNECT = 'ttm4115/team_1/project/connect'


class QrReader:
    def __init__(self):
        self.__mqtt_client = MqttClient("QrReader")

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
        ret, frame = camera.read()

        while ret:
            ret, frame = camera.read()
            frame = self.__read_barcodes(frame)
            cv2.imshow('Barcode/QR code reader', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        camera.release()
        cv2.destroyAllWindows()
