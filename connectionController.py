#Denne skal ha en fil der den kan finne/skrive til hvilken kontor som er koblet til /eller en database.
#den skal bruke MQTT til å mota og sende inforamsjon
#den kan endre hvem som er koblet til hvem etter succeful QR-kode scan, 
# og den kan svar hvis noen ønkser å vite hvem de er koblet til
import paho.mqtt.client as mqtt
import logging
import json

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883

MQTT_TOPIC_CONNECTION = "ttm4115/team_1/project/connectionController"

class connectionControllerComponent:
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug("MQTT connected to {}".format(client))

    def on_message(self, client, userdata, msg):
        if msg.topic == "ttm4115/team_1/project/connectionController":
            try:
                data = json.loads(msg.payload.decode("utf-8"))
            except Exception as err:
                self._logger.error("Message sent to topic {} had no valid JSON. Message ignored. {}".format(msg.topic, err))
                return
            if data["command"] == "who am I connected to?":
                if data["reciver"]=="connectionController":
                    #send et svar basert på hva som ligger i fila/databasen
                    #self.sendAnswer("who am I connected to?","office1","office2")
                    pass
            elif data["command"] == "change connetion":
                #lag den nye connection hvis det er mulig send feilmeldig hvis feil.
                #husk å send melding til den som den var koblet med fra før(hvis den var det)
                pass

    def __init__(self):

        self.name= "connectionController"

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
        self.mqtt_client.subscribe(MQTT_TOPIC_CONNECTION)
        # start the internal loop to process MQTT messages
        #self.mqtt_client.loop_start()
        self.mqtt_client.loop_forever()

    def sendAnswer(self,message, reciver,answer):
        command = {"command": message, "sender": self.name, "reciver": reciver,"answer": answer} 
        payload = json.dumps(command)
        self.mqtt_client.publish(MQTT_TOPIC_CONNECTION, payload)   

debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = connectionControllerComponent()