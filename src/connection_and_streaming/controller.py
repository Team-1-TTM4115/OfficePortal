from mqtt_client import MqttClient
import stmpy
import logging
import json
import time
from threading import Thread

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
            "target": "off",
        }

        t1 = {
            "trigger": "on",
            "source": "off",
            "target": "connected",
            "effect": "enter_gallery_mode",
            "function": self.check_connection
        }

        t2 = {
            "trigger": "new_connection",
            "source": "not_connected",
            "target": "connected",
            "effect": "sensor_on; log_in_connected",
        }

        t3 = {
            "trigger": "connection_successful",
            "source": "not_connected",
            "target": "waiting_for_partner",
            "effect": "sensor_on; send_change_connection; log_in_connected; start_timer('idle_timeout', 60000);",
        }
        t4 = {
            "trigger": "partner_left_connection",
            "source": "connected",
            "target": "not_connected",
            "effect": "sensor_off; start_listening; log_in_not_connected",
        }
        t5 = {
            "trigger": "movement_detected",
            "source": "connected",
            "target": "waiting_for_partner",
            "effect": "start_timer('idle_timeout', 60000); start_listening; log_in_waiting_for_partner",
        }

        t6 = {
            "trigger": "idle_timeout",
            "source": "waiting_for_partner",
            "target": "connected",
            "effect": "enter_gallery_mode; stop_listening; log_in_connected",
        }

        t7 = {
            "trigger": "partner_left_connection",
            "source": "waiting_for_partner",
            "target": "not_connected",
            "effect": "log_in_not_connected; enter_gallery_mode",
        }

        t8 = {
            "trigger": "partner_joined",
            "source": "waiting_for_partner",
            "target": "active_session",
            "effect": "log_in_active_session",
        }

        t9 = {
            "trigger": "idle_timeout",
            "source": "active_session",
            "target": "connected",
            "effect": "send_I_am_idle; enter_gallery_mode; stop_listening; log_in_connected",
        }
        t10 = {
            "trigger": "partner_idle",
            "source": "active_session",
            "target": "waiting_for_partner",
            "effect": "log_in_waiting_for_partner",
        }
        t11 = {
            "trigger": "new_connection",
            "source": "active_session",
            "target": "waiting_for_partner",
            "effect": "send_left_connection; log_in_waiting_for_partner",
        }
        t12 = {
            "trigger": "partner_left_connection",
            "source": "active_session",
            "target": "not_connected",
            "effect": "enter_gallery_mode; log_in_not_connected",
        }

        t13 = {
            "trigger": "connection_successful",
            "source": "active_session",
            "target": "waiting_for_partner",
            "effect": "send_change_connection;",
        }

        active_session = {'name': 'active_session',
                          'entry': 'send_partner_active; turn_on_reciver; vidoe_capture_on; turn_on_microphone; enter_video_call',
                          'exit': 'turn_reciver_off; vidoe_capture_off; turn_microphone_off',
                          'movement_detected': 'start_timer("idle_timeout", 60000)',
                          'change_connection': 'enter_qr_scanner',
                          'qr_fail': ' enter_video_call',
                          'change_session_view': 'trigger_change(*)',
                          'choose_filter': 'apply_filter(*)', }

        connected = {'name': 'connected',
                     'new_connection': 'send_left_connection', }

        waiting_for_partner = {'name': 'waiting_for_partner',
                               'entry': 'start_timer("resend_timer", 20000); send_partner_active; enter_waiting_mode; controller_is_listing',
                               'qr_code_scanned': 'send_left_connection',
                               'new_connection': 'send_left_connection',
                               'connection_successful': 'send_change_connection; send_partner_active;',
                               'resend_timer': 'send_partner_active; start_timer("resend_timer", 20000)',
                               'movement_detected': 'start_timer("idle_timeout", 60000)',
                               'change_connection': 'enter_qr_scanner',
                               'qr_fail': 'enter_waiting_mode',
                               'exit': 'controller_is_not_listing'}

        not_connected = {'name': 'not_connected',
                         'change_connection': 'enter_qr_scanner',
                         'qr_fail': 'enter_gallery_mode', }

        self.stm = stmpy.Machine(name=name,
                                 transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13],
                                 obj=self, states=[active_session, connected, waiting_for_partner, not_connected])

    def check_connection(self):
        """
        Check if the state is equal to connected
        """
        self.component.check_connection()
        time.sleep(0.5)
        if self.component.connection is None:
            self._logger.info("state=not_connected")
            self.start_listening()
            return "not_connected"
        else:
            self._logger.info("state=connected")
            self.sensor_on()
            return "connected"

    def controller_is_listing(self):
        self.component.listening_for_call = True

    def controller_is_not_listing(self):
        self.component.listening_for_call = True

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

    def stop_listening(self):
        self.component.stop_listening()

    def vidoe_capture_on(self):
        self.component.vidoe_capture_on()

    def vidoe_capture_off(self):
        self.component.vidoe_capture_off()

    def turn_on_reciver(self):
        self.component.turn_on_reciver()

    def turn_reciver_off(self):
        self.component.turn_reciver_off()

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

    def trigger_change(self, command):
        self.component.trigger_change(command)

    def apply_filter(self, command):
        self.component.apply_filter(command)


class ControllerComponent:

    def __init__(self, name):
        self.officeName = name
        self.connection = None

        self.listening_for_call = False

        # Here you the define which sensors
        self.sensor = self.officeName + "sensor"

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        debug_level = logging.DEBUG
        logger = logging.getLogger(__name__)
        logger.setLevel(debug_level)
        ch = logging.StreamHandler()
        ch.setLevel(debug_level)
        formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = MqttClient("Controller" + self.officeName)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(MQTT_TOPIC_SENSOR)
        self.mqtt_client.subscribe(MQTT_TOPIC_CONNECTION)
        self.mqtt_client.subscribe(MQTT_TOPIC_QR)
        self.mqtt_client.subscribe(MQTT_TOPIC_CONTROLLER)
        t = Thread()
        self.mqtt_client.loop_start()

        self.stm_driver = None
        # we start the stmpy driver, without any state machines for now
        controller = ControllerLogic('Controller', self)
        self.stm = controller.stm

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when connected to MQTT
        """
        self._logger.debug('MQTT connected to {}'.format(client))

    def load_json(self, msg):
        """
        Deserialize JSON message
        """
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        return data

    def on_message(self, client, userdata, msg):
        """
        Callback when a message is recieved through MQTT
        """
        if msg.topic == "ttm4115/team_1/project/sensor":
            data = self.load_json(msg)
            if data["sender"] == self.sensor and data["command"] == "movement":
                self.stm_driver.send("movement_detected", "Controller")
        elif msg.topic == 'ttm4115/team_1/project/connectionController':
            data = self.load_json(msg)
            if data["command"] == "new connection" and data["reciver"] == self.officeName:
                self.connection = data["answer"]
                self.stm_driver.send("new_connection", "Controller")
            elif data["command"] == "who am I connected to?":
                if data["sender"] == "connectionController" and data["reciver"] == self.officeName:
                    self.connection = data["answer"]
            elif data["command"] == "left connection":
                if data["sender"] == "connectionController" and data["reciver"] == self.officeName:
                    self.stm_driver.send("partner_left_connection", "Controller")
        elif msg.topic == "ttm4115/team_1/project/QR":
            data = self.load_json(msg)

            if data["command"] == "QRscansuccess" and data["reciver"] == self.officeName:
                self.connection = data["sender"]
                self.stm_driver.send("connection_successful", "Controller")
            elif data["command"] == "QRscanexpired" and data["reciver"] == self.officeName:
                self.stm_driver.send("qr_fail", "Controller")
        elif msg.topic == "ttm4115/team_1/project/controller":
            data = self.load_json(msg)
            if (data["command"] == "partner active" and data["sender"] == self.connection and
                    data["reciver"] == self.officeName and data["answer"] == "first" and self.listening_for_call):
                self.send_msg("partner active", self.officeName, self.connection, "Not first", MQTT_TOPIC_CONTROLLER)
                self.stm_driver.send("partner_joined", "Controller")
            elif data["command"] == "I am idle" and data["sender"] == self.connection and data[
                "reciver"] == self.officeName:
                self.stm_driver.send("partner_idle", "Controller")

    def stop(self):
        """
        Stop listening to MQTT messages
        :return:
        """
        self.mqtt_client.loop_stop()

    def send_change_connection(self):
        """
        Send MQTT message to connectionController topic to change connection
        """
        self.send_msg("change connetion", self.officeName, "connectionController", self.connection,
                      MQTT_TOPIC_CONNECTION)

    def check_connection(self):
        """
        Send MQTT message to connectionController topic to check who this office is connected to
        """
        self.send_msg("who am I connected to?", self.officeName, "connectionController", None, MQTT_TOPIC_CONNECTION)

    def send_left_connection(self):
        """
        Send MQTT message to connectionController topic when leaving a connection
        """
        self.send_msg("left connection", self.officeName, "connectionController", self.connection,
                      MQTT_TOPIC_CONNECTION)

    def send_partner_active(self):
        """
        Send MQTT message to connectionController topic to check if partner is active
        """
        self.send_msg("partner active", self.officeName, self.connection, "first", MQTT_TOPIC_CONTROLLER)

    def send_I_am_idle(self):
        """
        Send MQTT message to connectionController topic to tell partner that this office is now idle
        """
        self.send_msg("I am idle", self.officeName, self.connection, None, MQTT_TOPIC_CONTROLLER)

    def sensor_on(self):
        self.stm_driver.send("turn_sensor_on", "streamvideo")

    def send_msg(self, msg, sender, reciver, answer, where):
        """
        Serialize into JSON string and publish on topic
        :param where: Topic to publish on
        """
        command = {"command": msg, "sender": sender, "reciver": reciver, "answer": answer}
        payload = json.dumps(command)
        self.mqtt_client.publish(where, payload)

    def sensor_off(self):
        self.stm_driver.send("turn_sensor_off", "streamvideo")

    def vidoe_capture_off(self):
        self.stm_driver.send("turn_filter_off", "streamvideo")
        self.stm_driver.send("turn_background_off", "streamvideo")
        self.stm_driver.send("vidoe_capture_off", "streamvideo")

    def vidoe_capture_on(self):
        self.stm_driver.send("vidoe_capture_on", "streamvideo", kwargs={"send_to": self.connection + "reciver"})

    def turn_on_reciver(self):
        self.send_msg("streamstart", "Controller", self.officeName + "reciver", self.connection, MQTT_TOPIC_RECIVER)

    def turn_reciver_off(self):
        self.send_msg("streamstop", "Controller", self.officeName + "reciver", self.connection, MQTT_TOPIC_RECIVER)

    def turn_on_microphone(self):
        self.send_msg("streamstart", "Controller", self.officeName + "audio", self.connection + "reciver",
                      "ttm4115/team_1/project/audio" + self.officeName[-1])

    def turn_microphone_off(self):
        self.send_msg("streamstop", "Controller", self.officeName + "audio", self.connection + "reciver",
                      "ttm4115/team_1/project/audio" + self.officeName[-1])

    def enter_gallery_mode(self):
        self.stm_driver.send("enter_gallery_mode", "gui_stm")

    def enter_waiting_mode(self):
        self.stm_driver.send("enter_waiting_mode", "gui_stm")

    def enter_qr_scanner(self):
        self.stm_driver.send("enter_qr_scanner", "gui_stm")

    def enter_video_call(self):
        self.stm_driver.send("enter_video_call", "gui_stm")

    def start_listening(self):
        self.stm_driver.send("start_listening", "voice_stm")

    def stop_listening(self):
        self.stm_driver.send("stop_listening", "voice_stm")

    def trigger_change(self, command):
        """
        Check incoming voice command if it should open or close window
        """
        if command == "open menu":
            self.stm_driver.send("open_menu", "gui_stm")
        elif command == "close menu":
            self.stm_driver.send("close_menu", "gui_stm")

    def apply_filter(self, command):
        """
        Check incoming voice command if it should add a face filter or background filter
        """
        if command[0] == "background number":
            if command[1] == 1:
                effect = "easter"
            elif command[1] == 2:
                effect = "lofoten"
            elif command[1] == 3:
                effect = "vacay"
            self.stm_driver.send("turn_background_on", "streamvideo", kwargs={"effect": effect})
        elif command[0] == "face number":
            if command[1] == 1:
                effect = "dog"
            elif command[1] == 2:
                effect = "hat_glasses"
            self.stm_driver.send("turn_filter_on", "streamvideo", kwargs={"effect": effect})
        elif command[0] == "remove face":
            self.stm_driver.send("turn_filter_off", "streamvideo")
        elif command[0] == "remove background":
            self.stm_driver.send("turn_background_off", "streamvideo")
