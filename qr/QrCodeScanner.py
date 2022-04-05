import cv2
from pyzbar import pyzbar
from MqttClient import MqttClient

TOPIC_CONNECT = 'ttm4115/team_1/project/connect'

mqtt_client = MqttClient()


def read_barcodes(frame):
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        x, y, w, h = barcode.rect

        barcode_info = barcode.data.decode('utf-8')
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, barcode_info, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)

        mqtt_client.client.publish(TOPIC_CONNECT, barcode_info)

    return frame


camera = cv2.VideoCapture(0)
ret, frame = camera.read()

while ret:
    ret, frame = camera.read()
    frame = read_barcodes(frame)
    cv2.imshow('Barcode/QR code reader', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
camera.release()
cv2.destroyAllWindows()
