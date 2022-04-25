import paho.mqtt.client as mqtt
import logging
import json



MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883
FPS =30


MQTT_TOPIC_AUDIO = "ttm4115/team_1/project/audio"
MQTT_TOPIC_CAMERA = "ttm4115/team_1/project/camera"
MQTT_TOPIC_RECIVER = "ttm4115/team_1/project/reciver"

class sendstarttoall():
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug("MQTT connected to {}".format(client))

    def on_message(self, client, userdata, msg):
        pass
                   
    def __init__(self):


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
        # start the internal loop to process MQTT messages
        #self.send_msg("streamstart","Controller","office7reciver","office8",MQTT_TOPIC_RECIVER)
        #self.send_msg("streamstart","Controller","office8reciver","office7",MQTT_TOPIC_RECIVER)
        
        #self.send_msg("streamstart","Controller","office7camera","office8reciver","ttm4115/team_1/project/camera7")
        #self.send_msg("streamstart","Controller","office7audio","office8reciver","ttm4115/team_1/project/audio7")

        #self.send_msg("streamstart","Controller","office8camera","office7reciver","ttm4115/team_1/project/camera8")
        #self.send_msg("streamstart","Controller","office8audio","office7reciver","ttm4115/team_1/project/audio8")

        self.send_msg("backgorund_on","Controller","office7camera","lofoten","ttm4115/team_1/project/camera7")
        #self.send_msg("fliter_off","Controller","office1camera","hat_glasses","ttm4115/team_1/project/camera1")


        
        

    def send_msg(self,msg,sender,reciver,answer,where):
        command = {"command": msg, "sender": sender, "reciver": reciver,"answer": answer} 
        payload = json.dumps(command)
        self.mqtt_client.publish(where, payload)

t = sendstarttoall()