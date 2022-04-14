import uuid
from paho.mqtt.client import Client

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883


def on_connect(client, userdata, flags, rc):
    """ Default behaviour when connecting to a broker.
        Set MqttClient.on_connect to define your own behaviour """
    print('MQTT connected to {}'.format(client))


def on_message(client, userdata, message):
    """ Default behaviour when message is recieved from a subscribed topic.
        Set MqttClient.on_message to define your own behaviour """
    print("Message {} recieved from topic {}", message.payload.decode("utf-8"), message.topic)


class MqttClient(Client):
    """ Modified Mqtt Client for easier reuseability """
    def __init__(self, client_id=str(uuid.uuid4())):
        super().__init__(client_id)
        self.on_connect = on_connect
        self.on_message = on_message
        self.connect(MQTT_BROKER, MQTT_PORT)