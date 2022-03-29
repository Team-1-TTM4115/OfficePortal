#import test
import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = 'ttm4115/team_1/project/sensor1'


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

        self.stm = stmpy.Machine(name=name, transitions=[t0, t1,t2], obj=self)


    def turn_on_camera(self):
        print("turn_on_camera")
    def sensor_on(self):
        self.component.sensor_on()
    def turn_camera_off(self):
        print("turn_camera_off")
    def turn_display_on(turn_camera_off):
        print("turn_display_on")
    def show_static_picture(self):
        print("show_static_picture")



class ControllerComponent:
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        self.stm_driver.send("movement_detected", "Controller")  

    def __init__(self):
        
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
        # subscribe to proper topic(s) of your choice
        self.mqtt_client.subscribe(MQTT_TOPIC_INPUT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()


        # we start the stmpy driver, without any state machines for now
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        controller= ControllerLogic('Controller',self)
        self.stm_driver.add_machine(controller.stm)


    def stop(self):
        # stop the state machine Driver
        self.stm_driver.stop()

    def on_movement(self):
        print("on_movement")

    def sensor_on(self):
        #self.sensor = test.SensorMovementComponent()
        #self.sensor.Start_stmp()
        print("sensor_on")


debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = ControllerComponent()