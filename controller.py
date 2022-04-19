from mqtt_client import MqttClient
import stmpy
import logging
import json
import time
import keyboard

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883

MQTT_TOPIC_SENSOR = "ttm4115/team_1/project/sensor"
MQTT_TOPIC_CONNECTION = "ttm4115/team_1/project/connectionController"
MQTT_TOPIC_QR = "ttm4115/team_1/project/QR"
MQTT_TOPIC_CONTROLLER = "ttm4115/team_1/project/controller"
MQTT_TOPIC_RECIVER = "ttm4115/team_1/project/reciver"

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
            "effect": "start_timer('t', 60000); turn_on_QR; sensor_off; log_in_ready_for_qr_code",
        }
        t2 = {
            "trigger": "t",
            "source": "ready_for_qr_code",
            "target": "not_connected",
            "effect": "show_static_picture; turn_QR_off; sensor_on; log_in_not_connected",
        }

        t3 = {
            "trigger": "new_connection",
            "source": "not_connected",
            "target": "connected",
            "effect": "log_in_connected",
        }

        t4 = {
            "trigger": "new_connection",
            "source": "ready_for_qr_code",
            "target": "connected",
            "effect": "show_static_picture; turn_QR_off; sensor_on; log_in_connected",
        }

        t5 = {
            "trigger": "connection_successful",
            "source": "ready_for_qr_code",
            "target": "connected",
            "effect": "show_static_picture; turn_QR_off; sensor_on; send_change_connection; log_in_connected; ",
        }
        t6 = {
            "trigger": "partner_left_connection",
            "source": "connected",
            "target": "not_connected",
            "effect": "log_in_not_connected",
        }
        t7 = {
            "trigger": "new_connection",
            "source": "connected",
            "target": "connected",
            "effect": "send_left_connection; log_in_connected",
        }
        t8 = {
            "trigger": "movement_detected",
            "source": "connected",
            "target": "waiting_for_partner",
            "effect": "start_timer('idle_timeout', 60000); send_partner_avtive; start_timer('resend_timer', 20000); log_in_waiting_for_partner",
        }

        t9 = {
            "trigger": "idle_timeout",
            "source": "waiting_for_partner",
            "target": "connected",
            "effect": "log_in_connected; log_in_connected",
        }

        t10 = {
            "trigger": "new_connection",
            "source": "waiting_for_partner",
            "target": "connected",
            "effect": "send_left_connection; log_in_connected",
        }

        t11 = {
            "trigger": "partner_left_connection",
            "source": "waiting_for_partner",
            "target": "not_connected",
            "effect": "log_in_not_connected",
        }

        t12 = {
            "trigger": "resend_timer",
            "source": "waiting_for_partner",
            "target": "waiting_for_partner",
            "effect": "send_partner_avtive; start_timer('resend_timer', 20000); log_in_waiting_for_partner",
        }

        t13 = {
            "trigger": "movement_detected",
            "source": "waiting_for_partner",
            "target": "waiting_for_partner",
            "effect": "start_timer('idle_timeout', 60000); log_in_waiting_for_partner",
        }

        t14 = {
            "trigger": "partner_joined",
            "source": "waiting_for_partner",
            "target": "active_session",
            "effect": "send_partner_avtive; turn_on_reciver; turn_on_camera; turn_on_microphone; show_live_stream; log_in_active_session",
        }

        t15 = { 
            "trigger": "movement_detected",
            "source": "active_session",
            "target": "active_session",
            "effect": "start_timer('idle_timeout', 60000); log_in_active_session",
        }

        t16 = { 
            "trigger": "idle_timeout",
            "source": "active_session",
            "target": "connected",
            "effect": "send_I_am_idle; show_static_picture; turn_reciver_off; turn_camera_off; turn_microphone_off; log_in_connected",
        }
        t17 = { 
            "trigger": "partner_idle",
            "source": "active_session",
            "target": "waiting_for_partner",
            "effect": "send_partner_avtive; show_static_picture; turn_reciver_off; turn_camera_off; turn_microphone_off; start_timer('resend_timer', 20000); log_in_waiting_for_partner",
        }
        t18 = { 
            "trigger": "new_connection",
            "source": "active_session",
            "target": "connected",
            "effect": "send_left_connection; show_static_picture; turn_reciver_off; turn_camera_off; turn_microphone_off; log_in_connected",
        }
        t19 = {
            "trigger": "partner_left_connection",
            "source": "active_session",
            "target": "not_connected",
            "effect": "show_static_picture; turn_reciver_off; turn_camera_off; turn_microphone_off; log_in_not_connected",
        }
        t20 = {#qr_code_scanned er ikke lagt ennå, denne kan kansje være likt som i ready for qr code,
            "trigger": "qr_code_scanned",
            "source": "active_session",
            "target": "connected",
            "effect": "send_left_connection; show_static_picture; turn_reciver_off; turn_camera_off; turn_microphone_off; log_in_connected",
        }

        self.stm = stmpy.Machine(name=name, transitions=[t0, t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17,t18,t19,t20], obj=self)

    def check_connection(self):
        self.component.checkConnection()
        time.sleep(0.5)
        #ke skjer hvis connectioncontroller går på etter dette og
        # den hadde en connection(dette skal ikke skje med korrect bruk)
        if self.component.connection==None:
            self._logger.info("state=not_connected")
            return"not_connected"
        else:
            self._logger.info("state=connected")
            return "connected"

    def log_in_connected(self):
        self._logger.info("state=connected")

    def log_in_not_connected(self):
        self._logger.info("state=not_connected")

    def log_in_ready_for_qr_code(self):
        self._logger.info("state=ready_for_qr_code")

    def log_in_waiting_for_partner(self):
        self._logger.info("state=waiting_for_partner")

    def log_in_active_session(self):
        self._logger.info("state=active_session")

    def turn_on_microphone(self):
        self.component.turn_on_microphone()
    def turn_microphone_off(self):
        self.component.turn_microphone_off()

    def turn_on_camera(self):
        self.component.turn_on_camera()
    def turn_camera_off(self):
        self.component.turn_camera_off()

    def turn_on_reciver(self):
        self.component.turn_on_reciver()
    def turn_reciver_off(self):
        self.component.turn_reciver_off()

    def turn_on_QR(self):
        print("turn_on_QR")

    def turn_QR_off(self):
        print("turn_QR_off")

    def sensor_on(self):
        self.component.sensor_on()

    def sensor_off(self):
        self.component.sensor_off()

    def turn_display_on(self):
        #vis live, dette skal kanskje skje i QR/QIen.
        print("turn_display_on")
    def show_static_picture(self):
        #vise static
        print("show_static_picture")

    def show_live_stream(self):
        #vis live(hva du gjør), dette skal kanskje skje i QR/QI-en. revicer viser motparten
        pass

    def send_left_connection(self):
        self.component.send_left_connection()
    def send_change_connection(self):
        self.component.send_change_connection()

    def send_partner_avtive(self):
        self.component.send_partner_avtive()

    def send_I_am_idle(self):
        self.component.send_I_am_idle()

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

    def on_message(self, client, userdata, msg):
        if msg.topic == "ttm4115/team_1/project/sensor":
            data =self.loadjson(msg)
            if data["sender"] == self.sensor and data["command"] == "movement" :
                self.stm_driver.send("movement_detected", "Controller")  
        elif msg.topic == 'ttm4115/team_1/project/connectionController':
            data =self.loadjson(msg)
            #se på svaret på hvem du er koblet til 
            if data["command"] == "who am I connected to?":
                if data["sender"] == "connectionController" and data["reciver"] == self.officeName: 
                    self.connection= data["answer"]
            if data["command"] == "left connection":
                if data["sender"] == "connectionController" and data["reciver"] == self.officeName: 
                    self.stm_driver.send("partner_left_connection", "Controller")
        elif msg.topic == "ttm4115/team_1/project/QR":
            data =self.loadjson(msg)
            if data["command"] == "QRscansuccess" and data["sender"] =="QRCodeController" and data["reciver"] == self.officeName:
                self.connection = data["answer"]
                self.stm_driver.send("connection_successful", "Controller")
        elif msg.topic == "ttm4115/team_1/project/controller":
            data =self.loadjson(msg)
            if data["command"] == "partner active" and data["sender"] ==self.connection and data["reciver"] == self.officeName and data["answer"]=="first":
                self.send_msg("partner active",self.officeName,self.connection,"Not first",MQTT_TOPIC_CONTROLLER)
                self.stm_driver.send("partner_joined", "Controller")
            elif data["command"] == "I am idle" and data["sender"] ==self.connection and data["reciver"] == self.officeName:
                self.stm_driver.send("partner_idle", "Controller")

    def __init__(self):

        #Here is the office name
        self.officeName="office1"
        self.connection =None

        #Here you the define which sensors
        self.sensor=self.officeName+"sensor"
        
        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        # create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = MqttClient("Controller"+self.officeName)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(MQTT_TOPIC_SENSOR)
        self.mqtt_client.subscribe(MQTT_TOPIC_CONNECTION)
        self.mqtt_client.subscribe(MQTT_TOPIC_QR)
        self.mqtt_client.subscribe(MQTT_TOPIC_CONTROLLER)
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        controller= ControllerLogic('Controller',self)
        self.stm_driver.add_machine(controller.stm)
        while True:
            try:
                if keyboard.is_pressed("Escape"):
                    self.stop()
                    break
            except:
                pass

    def stop(self):
        # stop the state machine Driver and MQTT
        self.stm_driver.stop()
        self.mqtt_client.loop_stop()

    def send_change_connection(self):
        print("send_change_connection")
        self.send_msg("change connetion",self.officeName,"connectionController",self.connection,MQTT_TOPIC_CONNECTION)

    def checkConnection(self):
        self.send_msg("who am I connected to?",self.officeName,"connectionController",None,MQTT_TOPIC_CONNECTION)

    def send_left_connection(self):
        self.send_msg("left connection",self.officeName,"connectionController",self.connection,MQTT_TOPIC_CONNECTION)

    def send_partner_avtive(self):
        self.send_msg("partner active",self.officeName,self.connection,"first",MQTT_TOPIC_CONTROLLER)

    def send_I_am_idle(self):
        self.send_msg("I am idle",self.officeName,self.connection,None,MQTT_TOPIC_CONTROLLER)

    def sensor_on(self):
        #hva skjer hvis sensor ikke er på så den ikke blir skrudd på!!?
        self.send_msg("start",self.officeName,self.sensor,None,MQTT_TOPIC_SENSOR)
        print("sensor_on")

    def send_msg(self,msg,sender,reciver,answer,where):
        command = {"command": msg, "sender": sender, "reciver": reciver,"answer": answer} 
        payload = json.dumps(command)
        self.mqtt_client.publish(where, payload)

    def sensor_off(self):
        self.send_msg("stop",self.officeName,self.sensor,None,MQTT_TOPIC_SENSOR)
        print("sensor_off")

    def turn_camera_off(self):
        self.send_msg("streamstop","Controller",self.officeName+"camera",self.connection+"reciver","ttm4115/team_1/project/camera" +self.officeName[-1])
        print("turn_camera_off")

    def turn_on_camera(self):
        self.send_msg("streamstart","Controller",self.officeName+"camera",self.connection+"reciver","ttm4115/team_1/project/camera" +self.officeName[-1])
        print("turn_on_camera")
    
    def turn_on_reciver(self):
        self.send_msg("streamstart","Controller",self.officeName+"reciver",self.connection,MQTT_TOPIC_RECIVER)
        print("turn_on_reciver")
    def turn_reciver_off(self):
        self.send_msg("streamstop","Controller",self.officeName+"reciver",self.connection,MQTT_TOPIC_RECIVER)
        print("turn_reciver_off")

    def turn_on_microphone(self):
        self.send_msg("streamstart","Controller",self.officeName+"audio",self.connection+"reciver","ttm4115/team_1/project/audio"+self.officeName[-1])
        print("turn_on_reciver")
    def turn_microphone_off(self):
        self.send_msg("streamstop","Controller",self.officeName+"audio",self.connection+"reciver","ttm4115/team_1/project/audio"+self.officeName[-1])
        print("turn_reciver_off")

debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = ControllerComponent()