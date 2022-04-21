from mqtt_client import MqttClient
import logging
import json
# 

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883

MQTT_TOPIC_CONNECTION = "ttm4115/team_1/project/connectionController"

class connectionControllerComponent:
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug("MQTT connected to {}".format(client))

    def find_connetion(self,office):
        #finn hvilken kontor office har en conntetion med
        filereader = open("database.txt", "r")
        for connections in filereader:
            connection1, connection2= self.splitt_connections(connections)
            if connection1.strip() == office.strip():
                filereader.close
                return connection2.strip()
            elif connection2.strip()== office.strip():
                filereader.close
                return connection1.strip()
        filereader.close
        return None

    def splitt_connections(self,str):
        return str.split(";")[0],str.split(";")[1]

    def make_connection(self,office1,office2):
        filereader = open("database.txt", "r")
        connectionsList=[]
        for connections in filereader:
            connection1, connection2= self.splitt_connections(connections)
            if connection1 == office1 or connection2 == office1:
                connectionsList.append(office1+";"+office2+"\n")
            else:
                 connectionsList.append(connections+"\n")
        filereader.close
        str=""
        for connections in connectionsList:
            str=str+connections
        filewriter = open("database.txt", "w")
        filewriter.write(str)
        filewriter.close()

    def make_new_Connection(self,office1,office2):
        filereader = open("database.txt", "r")
        connectionsList=[]
        for connections in filereader:
            connectionsList.append(connections+"\n")
        filereader.close
        connectionsList.append(office1+";"+office2+"\n")
        str=""
        for connections in connectionsList:
            str=str+connections
        filewriter = open("database.txt", "w")
        filewriter.write(str)
        filewriter.close()

    def load_json(self, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        return data

    def on_message(self, client, userdata, msg):
        if msg.topic == "ttm4115/team_1/project/connectionController":
            data =self.load_json(msg)
            if data["command"] == "who am I connected to?":
                if data["reciver"]=="connectionController":
                    officeConntedTo = self.find_connetion(data["sender"])
                    self.send_answer("who am I connected to?",data["sender"],officeConntedTo)
            elif data["command"] == "change connetion":
                if data["reciver"]=="connectionController":
                    oldOffice = self.find_connetion(data["sender"])
                    if oldOffice != None:
                        self.make_connection(data["sender"],data["answer"])
                        self.send_answer("left connection",oldOffice,data["sender"])
                    else:
                        self.make_new_Connection(data["sender"],data["answer"])
            elif data["command"] == "left connection":
                if data["reciver"]=="connectionController":
                    self.send_answer("left connection",data["answer"],data["sender"])



    def __init__(self):

        self.name= "connectionController"

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
            except:
                pass
        

    def send_answer(self,msg, reciver,answer):
        self.send_msg(msg,self.name,reciver,answer) 

    def send_msg(self,msg,sender,reciver,answer):
        command = {"command": msg, "sender": sender, "reciver": reciver,"answer": answer} 
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