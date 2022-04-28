import keyboard

from mqtt_client import MqttClient
import logging
import json

#

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883

MQTT_TOPIC_CONNECTION = "ttm4115/team_1/project/connectionController"


class ConnectionControllerComponent:
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when connected to MQTT
        """
        self._logger.debug("MQTT connected to {}".format(client))

    def find_connetion(self, office):
        """
        Finds out if a connection with another office is already present in the database
        """
        filereader = open("database.txt", "r")
        for connections in filereader:
            connection1, connection2 = self.split_connections(connections)
            if connection1.strip() == office.strip():
                filereader.close()
                return connection2.strip()
            elif connection2.strip() == office.strip():
                filereader.close()
                return connection1.strip()
        filereader.close()
        return None

    def split_connections(self, string):
        """
        Split string in database to use for comparison
        """
        return string.split(";")[0], string.split(";")[1]

    def make_connection(self, office1, office2):
        """
        Save a connection between two offices in the database, overwriting existing connection
        """
        filereader = open("database.txt", "r")
        connections_list = []
        for connections in filereader:
            connection1, connection2 = self.split_connections(connections)
            if connection1 == office1 or connection2 == office1:
                connections_list.append(office1 + ";" + office2 + "\n")
            else:
                connections_list.append(connections + "\n")
        filereader.close()
        string = ""
        for connections in connections_list:
            string = string + connections
        filewriter = open("database.txt", "w")
        filewriter.write(string)
        filewriter.close()

    def make_new_connection(self, office1, office2):
        """
        Create an entirly new connection between two offices in the database
        """
        filereader = open("database.txt", "r")
        connections_list = []
        for connections in filereader:
            connections_list.append(connections + "\n")
        filereader.close()
        connections_list.append(office1 + ";" + office2 + "\n")
        string = ""
        for connections in connections_list:
            string = string + connections
        filewriter = open("database.txt", "w")
        filewriter.write(string)
        filewriter.close()

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
        if msg.topic == "ttm4115/team_1/project/connectionController":
            data = self.load_json(msg)
            if data["command"] == "who am I connected to?":
                if data["reciver"] == "connectionController":
                    office_connted_to = self.find_connetion(data["sender"])
                    self.send_answer("who am I connected to?", data["sender"], office_connted_to)
            elif data["command"] == "change connetion":
                if data["reciver"] == "connectionController":
                    old_office = self.find_connetion(data["sender"])
                    if old_office is not None:
                        self.make_connection(data["sender"], data["answer"])
                        self.send_answer("left connection", old_office, data["sender"])
                    else:
                        self.make_new_connection(data["sender"], data["answer"])
                    self.send_answer("new connection", data["answer"], data["sender"])
            elif data["command"] == "left connection":
                if data["reciver"] == "connectionController":
                    self.send_answer("left connection", data["answer"], data["sender"])

    def __init__(self):
        self.name = "connectionController"

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print("logging under name {}.".format(__name__))
        self._logger.info("Starting Component")

        # create a new MQTT client
        self._logger.debug("Connecting to MQTT broker {} at port {}".format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = MqttClient(self.name)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(MQTT_TOPIC_CONNECTION)
        self.mqtt_client.loop_start()
        while True:
            try:
                if keyboard.is_pressed("Escape"):
                    break
            except ValueError:
                print(self._logger.info("Multi-step hotkeys were pressed"))

    def send_answer(self, msg, reciver, answer):
        """
        Function for publishing a message through MQTT
        """
        self.send_msg(msg, self.name, reciver, answer)

    def send_msg(self, msg, sender, reciver, answer):
        """
        Serialize params into a JSON string and publish to MQTT
        """
        command = {"command": msg, "sender": sender, "reciver": reciver, "answer": answer}
        payload = json.dumps(command)
        self.mqtt_client.publish(MQTT_TOPIC_CONNECTION, payload)
