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
            "effect": "enter_gallery_mode",
            "function": self.check_connection
        }

        t1 = {
            "trigger": "new_connection",
            "source": "not_connected",
            "target": "connected",
            "effect": "sensor_on; log_in_connected",
        }

        t2 = { 
            "trigger": "connection_successful",
            "source": "not_connected",
            "target": "waiting_for_partner",
            "effect": "enter_waiting_mode; turn_QR_off; sensor_on; send_change_connection; send_partner_active; log_in_connected; start_timer('idle_timeout', 60000); start_timer('resend_timer', 20000)",
        }
        t3 = { 
            "trigger": "partner_left_connection",
            "source": "connected",
            "target": "not_connected",
            "effect": "sensor_off; start_listening; log_in_not_connected",
        }
        t4 = { 
            "trigger": "movement_detected",
            "source": "connected",
            "target": "waiting_for_partner",
            "effect": "start_timer('idle_timeout', 60000); start_listening; enter_waiting_mode; send_partner_active; start_timer('resend_timer', 20000); log_in_waiting_for_partner",
        }

        t5 = { 
            "trigger": "idle_timeout",
            "source": "waiting_for_partner",
            "target": "connected",
            "effect": "enter_gallery_mode; log_in_connected",
        }

        t6 = { 
            "trigger": "partner_left_connection",
            "source": "waiting_for_partner",
            "target": "not_connected",
            "effect": "log_in_not_connected; enter_gallery_mode",
        }

        t7 = { 
            "trigger": "partner_joined",
            "source": "waiting_for_partner",
            "target": "active_session",
            "effect": "log_in_active_session; enter_video_call",
        }

        t8 = { 
            "trigger": "idle_timeout",
            "source": "active_session",
            "target": "connected",
            "effect": "send_I_am_idle; enter_gallery_mode; stopp_listening; log_in_connected",
        }
        t9 = {
            "trigger": "partner_idle",
            "source": "active_session",
            "target": "waiting_for_partner",
            "effect": "send_partner_active; enter_waiting_mode; start_timer('resend_timer', 20000); log_in_waiting_for_partner",
        }
        t10 = {
            "trigger": "new_connection",
            "source": "active_session",
            "target": "waiting_for_partner",
            "effect": "send_left_connection; enter_waiting_mode; log_in_waiting_for_partner",
        }
        t11 = { 
            "trigger": "partner_left_connection",
            "source": "active_session",
            "target": "not_connected",
            "effect": "enter_gallery_mode; log_in_not_connected",
        }

        active_session = {'name': 'active_session',
        'entry':'send_partner_active; turn_on_reciver; turn_on_camera; turn_on_microphone',
        'exit':'turn_reciver_off; turn_camera_off; turn_microphone_off',
        'movement_detected': 'start_timer("idle_timeout", 60000)',
        'change_connection': 'turn_on_qr; enter_qr_scanner',
        'qr_fail': 'turn_off_qr; enter_video_call',
        'change_session_view': 'trigger_change(*)',
        'choose_filter' : 'apply_filter(*)',}

        connected = {'name': 'connected',
        'new_connection': 'send_left_connection; send_to_qui_connected',}

        waiting_for_partner = {'name': 'waiting_for_partner',
        'qr_code_scanned': 'send_left_connection',
        'new_connection': 'send_left_connection',
        'resend_timer': 'send_partner_active;start_timer("resend_timer", 20000)',
        'movement_detected':'start_timer("idle_timeout", 60000)',
        'change_connection': 'turn_on_qr; enter_qr_scanner',
        'qr_fail': 'turn_off_qr; enter_waiting_mode',}
        
        not_connected = {'name': 'not_connected',
        'change_connection': 'turn_on_qr; enter_qr_scanner',
        'qr_fail': 'turn_off_qr; enter_gallery_mode',}

        self.stm = stmpy.Machine(name=name, 
        transitions=[t0, t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11],
        obj=self, states=[active_session,connected,waiting_for_partner,not_connected])

    def check_connection(self):
        self.component.check_connection()
        time.sleep(0.5)
        #ke skjer hvis connectioncontroller går på etter dette og
        # den hadde en connection(dette skal ikke skje med korrect bruk)
        if self.component.connection==None:
            self._logger.info("state=not_connected")
            self.start_listening()
            return"not_connected"
        else:
            self._logger.info("state=connected")
            self.sensor_on()
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

    def start_listening(self):
        self.component.start_listening()
    def stopp_listening(self):
        self.component.stopp_listening()

    def turn_on_camera(self):
        self.component.turn_on_camera()
    def turn_camera_off(self):
        self.component.turn_camera_off()

    def turn_on_reciver(self):
        self.component.turn_on_reciver()
    def turn_reciver_off(self):
        self.component.turn_reciver_off()

    def turn_on_qr(self):
        print("turn_on_QR")

    def turn_qr_off(self):
        print("turn_QR_off")

    def sensor_on(self):
        self.component.sensor_on()

    def sensor_off(self):
        self.component.sensor_off()

    def enter_gallery_mode(self):
        self.component.enter_gallery_mode()
    def enter_waiting_mode(self):
        self.component.enter_waiting_mode()
    def enter_qr_scanner(self):
        self.component.enter_qr_scanner()
    def enter_video_call(self):
        self.component.enter_video_call()

    def send_start_qr(self):
        self.component.send_start_qr()
        
    def send_left_connection(self):
        self.component.send_left_connection()
    def send_change_connection(self):
        self.component.send_change_connection()

    def send_partner_active(self):
        self.component.send_partner_active()

    def send_I_am_idle(self):
        self.component.send_I_am_idle()

    def trigger_change(self,command):
        self.component.trigger_change(command)

    def apply_filter(self,command):
        self.component.apply_filter(command)


class ControllerComponent:
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug('MQTT connected to {}'.format(client))

    def load_json(self, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        return data

    def on_message(self, client, userdata, msg):
        if msg.topic == "ttm4115/team_1/project/sensor":
            data =self.load_json(msg)
            if data["sender"] == self.sensor and data["command"] == "movement" :
                self.stm_driver.send("movement_detected", "Controller")  
        elif msg.topic == 'ttm4115/team_1/project/connectionController':
            data =self.load_json(msg)
            #se på svaret på hvem du er koblet til 
            if data["command"] == "who am I connected to?":
                if data["sender"] == "connectionController" and data["reciver"] == self.officeName: 
                    self.connection= data["answer"]
            if data["command"] == "left connection":
                if data["sender"] == "connectionController" and data["reciver"] == self.officeName: 
                    self.stm_driver.send("partner_left_connection", "Controller")
        elif msg.topic == "ttm4115/team_1/project/QR":
            data =self.load_json(msg)

            if data["command"] == "QRscansuccess" and data["reciver"] == self.officeName:
                self.connection = data["sender"] 
                self.stm_driver.send("connection_successful", "Controller")
        elif msg.topic == "ttm4115/team_1/project/controller":
            data =self.load_json(msg)
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

        self.stm_driver = None
        # we start the stmpy driver, without any state machines for now
        #self.stm_driver = stmpy.Driver()
        #self.stm_driver.start(keep_active=True)
        controller= ControllerLogic('Controller',self)
        #self.stm_driver.add_machine(controller.stm)
        self.stm= controller.stm
#        while True:
#            try:
#                if keyboard.is_pressed("Escape"):
#                    self.stop()
#                    break
#            except:
#                pass


    def stop(self):
        # stop the state machine Driver and MQTT
        #self.stm_driver.stop()
        self.mqtt_client.loop_stop()

    def send_change_connection(self):
        print("send_change_connection")
        self.send_msg("change connetion",self.officeName,"connectionController",self.connection,MQTT_TOPIC_CONNECTION)

    def check_connection(self):
        self.send_msg("who am I connected to?",self.officeName,"connectionController",None,MQTT_TOPIC_CONNECTION)

    def send_left_connection(self):
        self.send_msg("left connection",self.officeName,"connectionController",self.connection,MQTT_TOPIC_CONNECTION)

    def send_partner_active(self):
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

    def enter_gallery_mode(self):
        pass
    def enter_waiting_mode(self):
        pass
    def enter_qr_scanner(self):
        pass
    def enter_video_call(self):
        pass

    def send_start_qr(self):
        print("jipp")
        pass

    def start_listening(self):
        self.stm_driver.send("start_listening", "voice_stm")
    def stopp_listening(self):
        self.stm_driver.send("stopp_listening", "voice_stm")

    def trigger_change(self,command):
        if command == "open menu":
            pass
        elif command == "close menu":
            pass

    def apply_filter(self,command):
        if command[1] ==1:
            effect = "dog"
        elif command[1] ==2:
            effect = "hat_glasses"
        elif command[1] ==3:
            effect = "easter"
        elif command[1] ==4:
            effect = "lofoten"
        elif command[1] ==5:
            effect = "vacay"
        if command[0]=="apply background filter number":
            self.send_msg("backgorund_on","Controller",self.officeName+"camera",effect,"ttm4115/team_1/project/camera" +self.officeName[-1])
        elif command[0]=="apply face filter number":
            self.send_msg("fliter_on","Controller",self.officeName+"camera",effect,"ttm4115/team_1/project/camera" +self.officeName[-1])
        elif command[0]=="remove face filter":
            self.send_msg("fliter_off","Controller",self.officeName+"camera",None,"ttm4115/team_1/project/camera" +self.officeName[-1])
        elif command[0]=="remove background filter":
            self.send_msg("backgorund_off","Controller",self.officeName+"camera",None,"ttm4115/team_1/project/camera" +self.officeName[-1])


debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = ControllerComponent()
t.stm_driver