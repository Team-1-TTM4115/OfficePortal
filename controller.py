#import test
from hashlib import new
from multiprocessing import connection
import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json
import time

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = 'ttm4115/team_1/project/sensor'
MQTT_TOPIC_CONNECTION = "ttm4115/team_1/project/connectionController"
MQTT_TOPIC_QR = "ttm4115/team_1/project/QR"


class ControllerLogic:


    def __init__(self, name, component):
        self._logger = logging.getLogger(__name__)
        self.name = name
        self.id = name
        self.component = component



        t0 = {
            "source": "initial",
            "target": "not_connected",
            "effect": "sensor_on; turn_display_on",
            "function": self.check_connection
        }
        t1 = {
            "trigger": "movement_detected",
            "source": "not_connected",
            "target": "ready_for_qr_code",
            "effect": "start_timer('t', 60000); turn_on_camera",
        }
        t2 = {
            "trigger": "t",
            "source": "ready_for_qr_code",
            "target": "not_connected",
            "effect": "show_static_picture; turn_camera_off",
        }

        t3 = {
            "trigger": "new_connection",
            "source": "not_connected",
            "target": "connected",
        }

        t4 = {
            "trigger": "new_connection",
            "source": "ready_for_qr_code",
            "target": "connected",
            "effect": "show_static_picture; turn_camera_off",
        }

        t5 = {
            "trigger": "connection_successful",
            "source": "ready_for_qr_code",
            "target": "connected",
            "effect": "show_static_picture; turn_camera_off",
        }
        t5 = {
            "trigger": "partner_left_connection",
            "source": "connected",
            "target": "not_connected",
        }
        t5 = {
            "trigger": "new_connection",
            "source": "connected",
            "target": "connected",
            "effect": "send_left_connection",
        }

        self.stm = stmpy.Machine(name=name, transitions=[t0, t1,t2,t3,t4,t5], obj=self)


    def check_connection(self):
        self.component.checkConnection()
        time.sleep(0.1)
        if self.component.connection==None:
            return 'not_connected'
        else:
            print("hei")
            return 'connected'

    def turn_on_camera(self):
        #turn on live
        print("turn_on_camera")
    def sensor_on(self):
        #skrue på sensor; nå skjer ikke dette 
        self.component.sensor_on()
    def turn_camera_off(self):
        #turn off live
        print("turn_camera_off")
    def turn_display_on(self):
        #hvis live
        self.component.sensor_off()
        print("turn_display_on")
    def show_static_picture(self):
        #vise static
        print("show_static_picture")
    def send_left_connection(self):
        #Må send meldig om at du har forlatt connection
        print("send_left_connection")



class ControllerComponent:
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug('MQTT connected to {}'.format(client))

    def loadjson(self, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        return data

    def checkConnection(self):
        command = {"command": "who am I connected to?", "sender": self.officeName, "reciver": "connectionController","answer": None} 
        payload = json.dumps(command)
        self.mqtt_client.publish(MQTT_TOPIC_CONNECTION, payload)   

    def on_message(self, client, userdata, msg):
        if msg.topic == 'ttm4115/team_1/project/sensor':
            data =self.loadjson(msg)
            if data['sensor'] == self.sensor:
                self.stm_driver.send("movement_detected", "Controller")  
        elif msg.topic == 'ttm4115/team_1/project/connectionController':
            data =self.loadjson(msg)
            #se på svaret på hvem du er koblet til 
            if data["command"] == "who am I connected to?":
                if data["sender"] == "connectionController" and data["reciver"] == self.officeName: 
                    self.connection= data["answer"]
        elif msg.topic == 'ttm4115/team_1/project/QR':
            data =self.loadjson(msg)
            if data["msg"] == "success":
                self.stm_driver.send("connection_successful", "Controller")


    def __init__(self):

        #Here is the office name
        self.officeName="office1"
        self.connection =None

        #Here you the define which sensors
        self.sensor="sensor1"
        
        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # subscribe to topics
        self.mqtt_client.subscribe(MQTT_TOPIC_INPUT)
        self.mqtt_client.subscribe(MQTT_TOPIC_CONNECTION)
        self.mqtt_client.subscribe(MQTT_TOPIC_QR)
        
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        controller= ControllerLogic('Controller',self)
        self.stm_driver.add_machine(controller.stm)


    def stop(self):
        # stop the state machine Driver and MQTT
        self.stm_driver.stop()
        self.mqtt_client.loop_stop()



    def sensor_on(self):
        print("sensor_on")

    def sensor_off(self):
        print("sensor_off")


debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = ControllerComponent()