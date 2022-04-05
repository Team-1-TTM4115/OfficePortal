import paho.mqtt.client as mqtt
import logging

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883


class MqttClient:
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug('MQTT connected to {}'.format(client))
        print('MQTT connected to {}'.format(client))

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.client = mqtt.Client("Office_Portal")

        self.client.on_connect = self.on_connect
        self.client.connect(MQTT_BROKER, MQTT_PORT)

        #self.client.loop_start()
