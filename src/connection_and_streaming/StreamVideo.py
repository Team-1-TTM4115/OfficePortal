from mqtt_client import MqttClient
import logging
import json
import keyboard
import cv2
import numpy as np
import base64
from threading import Thread
import time 

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883
FPS =30
sleeping=False

MQTT_TOPIC_SENSOR = 'ttm4115/team_1/project/sensor'

class StreamVideo:
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug("MQTT connected to {}".format(client))

    def loadjson(self, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        return data

    def on_message(self, client, userdata, msg): 
        if msg.topic == 'ttm4115/team_1/project/camera'+str(self.number):
            data =self.loadjson(msg)
            if data["command"] == "streamstart" and data["reciver"]== self.name+"camera":
                self.video_on = True
                self.sendTo =data["answer"]
            elif data["command"] == "streamstop" and data["reciver"]== self.name+"camera":
                self.video_on = False
        elif msg.topic == 'ttm4115/team_1/project/sensor':
            data =self.loadjson(msg)
            if (self.sensor_on == False) and data["reciver"]== self.name+"sensor":
                if data["command"] == "start":
                    self.office = data["sender"]
                    self.sensor_on =True
            if (self.sensor_on == True) and (data["reciver"]== self.name+"sensor") and ((data["sender"]== self.office) ):
                if data["command"] == "stop":
                    self.sensor_on =False

    def bts_to_frame(self,b64_string):
        base64_bytes=b64_string.encode("utf-8")
        buff = np.frombuffer(base64.b64decode(base64_bytes), np.uint8)
        img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
        return img

    def __init__(self):
        self.number =1
        self.name= "office"+str(self.number)
        self.sendTo =None
        self.active =False
        self.on=True
        self.sensor_on =False
        self.video_on =False

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print("logging under name {}.".format(__name__))
        self._logger.info("Starting Component")

        # create a new MQTT client
        self._logger.debug("Connecting to MQTT broker {} at port {}".format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = MqttClient("StreamVideo"+self.name)
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe("ttm4115/team_1/project/camera"+str(self.number))
        self.mqtt_client.subscribe(MQTT_TOPIC_SENSOR)
        # start the internal loop to process MQTT messages
        thread = Thread(target=self.mqtt_client.loop_start())
        thread.start()

        cap = cv2.VideoCapture(0)
        _,frame = cap.read()
        time.sleep(1)
        framelast=frame 
        self.time_1 = time.time()
        self.time_2 = time.time()
        sleep =time.time()
    
        self.count=0
        while self.on:
            while self.video_on or self.sensor_on:
                self.active= self.exit()
                _,frame = cap.read()
                if self.video_on==True:
                    self.sendVideo(frame)
                if self.sensor_on==True and (time.time()-sleep)>5: #kansje øk med mer
                    self.sensor(frame,framelast)
                    sleep=time.time()
                framelast=frame
                quit=self.exit()
                if quit==False:
                    break

                
            self.on=self.exit()
        self.mqtt_client.loop_stop()
        cap.release()        
        cv2.destroyAllWindows()


    def sendVideo(self,frame):
        image_bytes = cv2.imencode('.jpg', frame)[1]
        b64_bytes = base64.b64encode(image_bytes)
        b64_string = b64_bytes.decode("utf-8")
        timestamp=str(int(time.time()*1000))
        self.count=self.count+1
        #print("count "+str(self.count)+" tid "+ timestamp)
        self.send_msg("streamvideo","office"+str(self.number)+"camera",self.sendTo,timestamp,b64_string,"ttm4115/team_1/project/camera"+str(self.number))

        time.sleep(1 / FPS)


    def sensor(self,frame1,frame2):
        diff = cv2.absdiff(frame1,frame2)
        gray= cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(5,5),0)
        _, threshHold= cv2.threshold(blur, 20,255,cv2.THRESH_BINARY)
        dilated =cv2.dilate(threshHold,None,iterations=3)
        contours,_= cv2.findContours(dilated,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        movent=False
        for contour in contours:
            if cv2.contourArea(contour)>700:
                movent=True
        frame1=frame2
        self.time_2 = time.time()
        if (self.time_2 - self.time_1)>1:
            self.time_1 = time.time()
            if movent==True:
                timestamp=str(int(time.time()*1000))
                self.send_msg("movement",self.name+"sensor",self.office,timestamp,None,MQTT_TOPIC_SENSOR)


    def exit(self):
        try:
            if keyboard.is_pressed("Escape"):
                return False
            else:
                return True
        except:
            pass
        
    def send_msg(self,msg,sender,reciver,timestamp,answer,where):
        command = {"command": msg, "sender": sender, "reciver": reciver,"time": timestamp,"answer": answer} 
        payload = json.dumps(command)
        self.mqtt_client.publish(where, payload)

debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = StreamVideo()