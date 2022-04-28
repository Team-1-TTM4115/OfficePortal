from mqtt_client import MqttClient
import logging
import json

import cv2
import numpy as np
import base64
from threading import Thread
import time
import os
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import stmpy

from gui.camera import Camera

MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883
FPS =20

MQTT_TOPIC_SENSOR = 'ttm4115/team_1/project/sensor'

class StreamCapLogic:
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
            "trigger": "turn_sensor_on",
            "source": "off",
            "target": "sensor_on",
            "effect": "start_timer('sensor_timer', 5000)",
        }
        t2 = {
            "trigger": "turn_sensor_off;",
            "source": "sensor_on",
            "target": "off",
        }
        t3 = {
            "trigger": "vidoe_capture_on",
            "source": "sensor_on",
            "target": "sensor_and_live_on",
            "effect": "capture_on(*); start_timer('camera_timer', 200)",
        }
        t4 = {
            "trigger": "vidoe_capture_off",
            "source": "sensor_and_live_on",
            "target": "sensor_on",
            }
        t5 = {
            "trigger": "turn_filter_on",
            "source": "sensor_and_live_on",
            "target": "fliter_on",
            "effect": "fliter_on(*)",
            }
        t6 = {
            "trigger": "turn_filter_off",
            "source": "fliter_on",
            "target": "sensor_and_live_on",
            "effect": "fliter_off",
            }
        t7 = {
            "trigger": "turn_background_on",
            "source": "sensor_and_live_on",
            "target": "background_on",
            "effect": "background_on(*)",
            }
        t8 = {
            "trigger": "turn_background_off",
            "source": "background_on",
            "target": "sensor_and_live_on",
            "effect": "background_off",
            }
        t9 = {
            "trigger": "turn_filter_on",
            "source": "background_on",
            "target": "both_on",
            "effect": "fliter_on(*)",
            }
        t10 = {
            "trigger": "turn_filter_off",
            "source": "both_on",
            "target": "background_on",
            "effect": "fliter_off",
            }
        t11 = {
            "trigger": "turn_background_on",
            "source": "fliter_on",
            "target": "both_on",
            "effect": "background_on(*)",
            }
        t12 = {
            "trigger": "turn_background_off",
            "source": "both_on",
            "target": "fliter_on",
            "effect": "background_off",
            }
        

        sensor_on = {"name": "sensor_on",
        "sensor_timer": "start_timer('sensor_timer', 5000); check_movement",}
        sensor_and_live_on = {"name": "sensor_and_live_on",
        "camera_timer": "start_timer('camera_timer', 200); send_frame",
        "sensor_timer": "start_timer('sensor_timer', 5000); check_movement",}
        fliter_on = {"name": "fliter_on",
        "camera_timer": "start_timer('camera_timer', 100); send_frame",
        "sensor_timer": "start_timer('sensor_timer', 5000); check_movement",}
        background_on = {"name": "background_on",
        "camera_timer": "start_timer('camera_timer', 100); send_frame",
        "sensor_timer": "start_timer('sensor_timer', 5000); check_movement",}
        both_on = {"name": "both_on",
        "camera_timer": "start_timer('camera_timer', 100); send_frame",
        "sensor_timer": "start_timer('sensor_timer', 5000); check_movement",}

        self.stm = stmpy.Machine(name=name, 
        transitions=[t0,t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12],
        obj=self, states=[sensor_on,sensor_and_live_on,background_on,fliter_on,both_on])

    def send_frame(self):
        self.component.send_frame()

    def check_movement(self):
        self.component.check_movement()

    def background_on(self,effect):
        self.component.background =effect
    def background_off(self):
        self.component.background =None
    def fliter_on(self,effect):
        self.component.filter =effect
    def fliter_on(self):
        self.component.filter =None
    def capture_on(self,send_to):
        self.component.send_to= send_to
        

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
                self.send_to = data["answer"]
                self.stm_driver.send("vidoe_capture_on", "streamvideo")
            elif data["command"] == "streamstop" and data["reciver"] == self.name + "camera":
                self.video_on = False
                self.filter = None
                self.background = None
                if self.sensor_on==False:
                    self.stm_driver.send("vidoe_capture_off", "streamvideo")
            elif data["command"] == "fliter_on" and data["reciver"] == self.name + "camera":
                self.filter = data["answer"]
            elif data["command"] == "fliter_off" and data["reciver"] == self.name + "camera":
                self.filter = None
            elif data["command"] == "backgorund_on" and data["reciver"] == self.name + "camera":
                self.background = data["answer"]
                if self.background == "easter":
                    self.indexImg = 0
                elif self.background == "lofoten":
                    self.indexImg = 1
                elif self.background == "vacay":
                    self.indexImg = 2
            elif data["command"] == "backgorund_off" and data["reciver"] == self.name + "camera":
                self.background = None
        elif msg.topic == 'ttm4115/team_1/project/sensor':
            data =self.load_json(msg)
            if (self.sensor_on == False) and data["reciver"]== self.name+"sensor":
                if data["command"] == "start":
                    self.office = data["sender"]
                    self.sensor_on = True
                    self.stm_driver.send("turn_sensor_on", "streamvideo")
            if (self.sensor_on == True) and (data["reciver"] == self.name + "sensor") and (
            (data["sender"] == self.office)):
                if data["command"] == "stop":
                    self.sensor_on =False
                    if self.video_on== False:
                        self.stm_driver.send("turn_sensor_off", "streamvideo")
        #elif msg.topic == 'ttm4115/team_1/project/QR'+str(self.number):
        #    data =self.load_json(msg)
        #    if data["command"] == "start":
        #        self.QR_on=True
        #    elif data["command"] == "stop":
        #        self.QR_on=False


    def bts_to_frame(self,b64_string):
        base64_bytes=b64_string.encode("utf-8")
        buff = np.frombuffer(base64.b64decode(base64_bytes), np.uint8)
        img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
        return img

    def put_dog_filter(self, dog, fc, x, y, w, h):
        face_width = w
        face_height = h
        # resizing the pictures/filters to fit the face properties
        dog = cv2.resize(dog, (int(face_width * 1.5), int(face_height * 1.95)))
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

    def put_glass(self, glass, fc, x, y, w, h):
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

    def initialize_stm(self,cap,name):
        self.number =name[-1]
        self.name= name#"office"+str(self.number)
        self.send_to =None
        self.active =False
        self.on=True
        self.sensor_on =False
        self.video_on =False
        self.QR_on=False

        # Fliter
        self.face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.hat = cv2.imread(
            r'C:\Users\ingeb\Documents\universtiet\NTNU\tredje\var\Desgin\project_design\OfficePortal\src\connection_and_streaming\hat.png')
        self.glass = cv2.imread(
            r'C:\Users\ingeb\Documents\universtiet\NTNU\tredje\var\Desgin\project_design\OfficePortal\src\connection_and_streaming\glasses.png')
        self.dog = cv2.imread(
            r'C:\Users\ingeb\Documents\universtiet\NTNU\tredje\var\Desgin\project_design\OfficePortal\src\connection_and_streaming\dog.png')
        self.filter = None

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
        #self.mqtt_client.subscribe("ttm4115/team_1/project/camera"+str(self.number))
        #self.mqtt_client.subscribe("ttm4115/team_1/project/QR"+str(self.number))
        #self.mqtt_client.subscribe(MQTT_TOPIC_SENSOR)
        #thread = Thread(target=self.mqtt_client.loop_start())
        #thread.start()
        
        self.cap = cap#Camera(0,cv2.CAP_DSHOW)
        self.segmentor = SelfiSegmentation()
        self.listImg = os.listdir(r"C:\Users\ingeb\Documents\universtiet\NTNU\tredje\var\Desgin\project_design\OfficePortal\src\connection_and_streaming\BackgroundFilters")
        listImg = os.listdir(r"C:\Users\ingeb\Documents\universtiet\NTNU\tredje\var\Desgin\project_design\OfficePortal\src\connection_and_streaming\BackgroundFilters")
        self.imgList = []
        self.background = None

        for imgPath in listImg:
            path = 'C:/Users/ingeb/Documents/universtiet/NTNU/tredje/var/Desgin/project_design/OfficePortal/src/connection_and_streaming/BackgroundFilters'
            imagePath = os.path.join(path, imgPath)
            img = cv2.imread(imagePath)
            self.imgList.append(img)

        _,frame = self.cap.read()
        self.framelast=frame 
        #self.time_1 = time.time()
        #self.time_2 = time.time()
        #self.sleep =time.time()
        #self.start(cap)

        self.stm_driver =None
        controller= StreamCapLogic('streamvideo',self)
        self.stm= controller.stm

    def send_frame(self):
        _,frame = self.cap.read()
        self.send_video(frame)
        

    def check_movement(self):
        _,frame = self.cap.read()
        self.sensor(frame,self.framelast)
        #self.sleep=time.time()
        self.framelast=frame


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
                    #self.sleep=time.time()

                self.framelast=frame
                quit=self.exit()
                if quit==False:
                    break

            self.on = self.exit()
        self.mqtt_client.loop_stop()
        cap.release()
        cv2.destroyAllWindows()


    def send_video(self,frame):
        if self.filter !=None:
            #frame = cv2.flip(frame, 1, 0)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fl = self.face.detectMultiScale(gray, 1.19, 7)
            for (x, y, w, h) in fl:
                if (self.filter == "hat_glasses"):
                    frame = self.put_hat(self.hat, frame, x, y, w, h)
                    frame = self.put_glass(self.glass, frame, x, y, w, h)
                elif self.filter == "dog":
                    frame = self.put_dog_filter(self.dog, frame, x, y, w, h)
        if self.background !=None:
            if self.background == "easter":
                self.indexImg = 0
            elif self.background == "lofoten":
                self.indexImg = 1
            elif self.background == "vacay":
                self.indexImg = 2
            #frame = cv2.flip(frame, 1, 0)
            frame = self.segmentor.removeBG(frame, self.imgList[self.indexImg], threshold=0.8)
        b64_string = self.frame_to_string(frame)
        timestamp=str(int(time.time()*1000))
        self.send_msg("streamvideo","office"+str(self.number)+"camera",self.send_to,timestamp,b64_string,"ttm4115/team_1/project/camera"+str(self.number))
        #time.sleep(1 / FPS)

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
            if cv2.contourArea(contour) > 700:
                movent = True
        #frame1 = frame2
        #self.time_2 = time.time()
        #if (self.time_2 - self.time_1) > 1:
            #self.time_1 = time.time()
        if movent == True:
            #timestamp = str(int(time.time() * 1000))
            #self.send_msg("movement", self.name + "sensor", self.office, timestamp, None, MQTT_TOPIC_SENSOR)
            self.stm_driver.send("movement_detected", "Controller")

    def exit(self):
        try:
            if False:# keyboard.is_pressed("Escape"):
                return False
            else:
                return True
        except:
            pass

    def send_msg(self, msg, sender, reciver, timestamp, answer, where):
        command = {"command": msg, "sender": sender, "reciver": reciver, "time": timestamp, "answer": answer}
        payload = json.dumps(command)
        self.mqtt_client.publish(where, payload)

if __name__ =="__main__":

    debug_level = logging.DEBUG
    logger = logging.getLogger(__name__)
    logger.setLevel(debug_level)
    ch = logging.StreamHandler()
    ch.setLevel(debug_level)
    formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    t = StreamVideo()
