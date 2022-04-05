import paho.mqtt.client as mqtt
import logging
import json

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883

MQTT_TOPIC_OUTPUT = "ttm4115/team_1/project/QR"

class QRCodeController:


    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug("MQTT connected to {}".format(client))

    def on_message(self, client, userdata, msg):
        pass

    def __init__(self):

        self.name= "QRCodeController"

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print("logging under name {}.".format(__name__))
        self._logger.info("Starting Component")

        # create a new MQTT client
        self._logger.debug("Connecting to MQTT broker {} at port {}".format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(MQTT_TOPIC_OUTPUT )
        # start the internal loop to process MQTT messages
        #self.mqtt_client.loop_start()
        self.sendAnswer("success")

    def sendAnswer(self,message):
        command = {"msg": message} 
        payload = json.dumps(command)
        self.mqtt_client.publish(MQTT_TOPIC_OUTPUT , payload)   

debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = QRCodeController()