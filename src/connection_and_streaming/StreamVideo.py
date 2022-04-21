from mqtt_client import MqttClient
import logging
import json
import keyboard
import cv2
import numpy as np
import base64
from threading import Thread
import time 
import os
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883
FPS =30

MQTT_TOPIC_SENSOR = 'ttm4115/team_1/project/sensor'

class StreamVideo:
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug("MQTT connected to {}".format(client))

    def load_json(self, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        return data

    def on_message(self, client, userdata, msg): 
        if msg.topic == 'ttm4115/team_1/project/camera'+str(self.number):
            data =self.load_json(msg)
            if data["command"] == "streamstart" and data["reciver"]== self.name+"camera":
                self.video_on = True
                self.sendTo =data["answer"]
            elif data["command"] == "streamstop" and data["reciver"]== self.name+"camera":
                self.video_on = False
                self.filter =None
                self.background =None
            elif data["command"] == "fliter_on" and data["reciver"]== self.name+"camera":
               self.filter = data["answer"]
            elif data["command"] == "fliter_off" and data["reciver"]== self.name+"camera":
                self.filter =None
            elif data["command"] == "backgorund_on" and data["reciver"]== self.name+"camera":
                self.background = data["answer"]
                if self.background== "easter":
                    self.indexImg =0
                elif self.background== "lofoten":
                    self.indexImg =1
                elif self.background== "vacay":
                    self.indexImg =2
            elif data["command"] == "backgorund_off" and data["reciver"]== self.name+"camera":
                self.background =None
        elif msg.topic == 'ttm4115/team_1/project/sensor':
            data =self.load_json(msg)
            if (self.sensor_on == False) and data["reciver"]== self.name+"sensor":
                if data["command"] == "start":
                    self.office = data["sender"]
                    self.sensor_on =True
            if (self.sensor_on == True) and (data["reciver"]== self.name+"sensor") and ((data["sender"]== self.office) ):
                if data["command"] == "stop":
                    self.sensor_on =False
        elif msg.topic == 'ttm4115/team_1/project/QR'+str(self.number):
            data =self.load_json(msg)
            if data["command"] == "start":
                self.QR_on=True
            elif data["command"] == "stop":
                self.QR_on=False


    def bts_to_frame(self,b64_string):
        base64_bytes=b64_string.encode("utf-8")
        buff = np.frombuffer(base64.b64decode(base64_bytes), np.uint8)
        img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
        return img


    def put_dog_filter(self,dog, fc, x, y, w, h):
        face_width = w
        face_height = h
        #resizing the pictures/filters to fit the face properties
        dog = cv2.resize(dog, (int(face_width*1.5), int(face_height *1.95)))
        for i in range(int(face_height * 1.75)):
            for j in range(int(face_width * 1.5)):
                for k in range(3):
                    if dog[i][j][k] < 235:
                        fc[y + i - int(0.375 * h) - 1][x + j - int(0.35 * w)][k] = dog[i][j][k]
        return fc

    def put_hat(self, hat, fc, x, y, w, h):
        face_width = w
        face_height = h

        hat_width = face_width + 1
        hat_height = int(0.50 * face_height) + 1

        hat = cv2.resize(hat, (hat_width, hat_height))

        for i in range(hat_height):
            for j in range(hat_width):
                for k in range(3):
                    if hat[i][j][k] < 235:
                        fc[y + i - int(0.40 * face_height)][x + j][k] = hat[i][j][k]
        return fc


    def put_glass(self,glass, fc, x, y, w, h):
        face_width = w
        face_height = h

        hat_width = face_width + 1
        hat_height = int(0.50 * face_height) + 1

        glass = cv2.resize(glass, (hat_width, hat_height))

        for i in range(hat_height):
            for j in range(hat_width):
                for k in range(3):
                    if glass[i][j][k] < 235:
                        fc[y + i - int(-0.20 * face_height)][x + j][k] = glass[i][j][k]
        return fc

    def __init__(self):
        self.number =1
        self.name= "office"+str(self.number)
        self.sendTo =None
        self.active =False
        self.on=True
        self.sensor_on =False
        self.video_on =False
        self.QR_on=False

        #Fliter
        self.face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.hat=cv2.imread(r'C:\Users\ingeb\Documents\universtiet\NTNU\tredje\var\Desgin\project_design\OfficePortal\src\I+E\hat.png')
        self.glass=cv2.imread(r'C:\Users\ingeb\Documents\universtiet\NTNU\tredje\var\Desgin\project_design\OfficePortal\src\I+E\glasses.png')
        self.dog= cv2.imread(r'C:\Users\ingeb\Documents\universtiet\NTNU\tredje\var\Desgin\project_design\OfficePortal\src\I+E\dog.png')
        self.filter =None

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print("logging under name {}.".format(__name__))
        self._logger.info("Starting Component")

        # create a new MQTT client
        self._logger.debug("Connecting to MQTT broker {} at port {}".format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = MqttClient("StreamVideo"+self.name)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe("ttm4115/team_1/project/camera"+str(self.number))
        self.mqtt_client.subscribe("ttm4115/team_1/project/QR"+str(self.number))
        self.mqtt_client.subscribe(MQTT_TOPIC_SENSOR)
        thread = Thread(target=self.mqtt_client.loop_start())
        thread.start()

        cap = cv2.VideoCapture(0)
        self.segmentor = SelfiSegmentation()
        self.listImg = os.listdir(r"C:\Users\ingeb\Documents\universtiet\NTNU\tredje\var\Desgin\project_design\OfficePortal\src\I+E\BackgroundFilters")
        listImg = os.listdir(r"C:\Users\ingeb\Documents\universtiet\NTNU\tredje\var\Desgin\project_design\OfficePortal\src\I+E\BackgroundFilters")
        self.imgList = []
        self.background =None

        for imgPath in listImg:
            path= 'C:/Users/ingeb/Documents/universtiet/NTNU/tredje/var/Desgin/project_design/OfficePortal/src/I+E/BackgroundFilters'
            imagePath= os.path.join(path, imgPath)
            img = cv2.imread(imagePath)
            self.imgList.append(img)

        _,frame = cap.read()
        time.sleep(1)
        self.framelast=frame 
        self.time_1 = time.time()
        self.time_2 = time.time()
        self.sleep =time.time()
        self.start(cap)

    def start(self,cap):
        while self.on:
            while self.video_on or self.sensor_on:
                self.active= self.exit()
                _,frame = cap.read()
                if self.video_on==True:
                    self.send_video(frame)
                if self.QR_on == True:
                    b64_string = self.frame_to_string(frame)
                    self.send_msg("QR",self.name+"QR","office"+str(self.number),None,b64_string,"ttm4115/team_1/project/QR"+str(self.number))
                if self.sensor_on==True and (time.time()-self.sleep)>5: #kansje øk med mer
                    self.sensor(frame,self.framelast)
                    self.sleep=time.time()

                self.framelast=frame
                quit=self.exit()
                if quit==False:
                    break

                
            self.on=self.exit()
        self.mqtt_client.loop_stop()
        cap.release()        
        cv2.destroyAllWindows()


    def send_video(self,frame):
        if self.filter !=None:
            #frame = cv2.flip(frame, 1, 0)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fl = self.face.detectMultiScale(gray,1.19,7)
            for (x, y, w, h) in fl:
                if (self.filter == "hat_glasses"):
                    frame = self.put_hat(self.hat, frame, x, y, w, h)
                    frame = self.put_glass(self.glass, frame, x, y, w, h)
                elif self.filter == "dog":
                    frame = self.put_dog_filter(self.dog, frame, x, y, w, h)
        if self.background !=None:
            #frame = cv2.flip(frame, 1, 0)
            frame = self.segmentor.removeBG(frame, self.imgList[self.indexImg], threshold=0.8)
        b64_string = self.frame_to_string(frame)
        timestamp=str(int(time.time()*1000))
        self.send_msg("streamvideo","office"+str(self.number)+"camera",self.sendTo,timestamp,b64_string,"ttm4115/team_1/project/camera"+str(self.number))
        time.sleep(1 / FPS)

    def frame_to_string(self, frame):
        image_bytes = cv2.imencode('.jpg', frame)[1]
        b64_bytes = base64.b64encode(image_bytes)
        b64_string = b64_bytes.decode("utf-8")
        return b64_string

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