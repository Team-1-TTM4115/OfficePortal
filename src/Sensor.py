import cv2
import paho.mqtt.client as mqtt
import logging
import time

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_OUTPUT = 'ttm4115/team_1/project/sensor'



class SensorMovement:

    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        pass

    def __init__(self):
        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        # create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()
        self.start()

    def start(self):
        time_1 = time.time()
        time_2 = time.time()
        cap = cv2.VideoCapture(0)
        ret, frame1 = cap.read()
        ret, frame2 = cap.read()
        while True:
            #finds the diffrent beteween the two frames find the contours
            diff = cv2.absdiff(frame1,frame2)
            gray= cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray,(5,5),0)
            _, threshHold= cv2.threshold(blur, 20,255,cv2.THRESH_BINARY)
            dilated =cv2.dilate(threshHold,None,iterations=3)
            contours,_= cv2.findContours(dilated,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

            #Check if the contours are bigger than 700 else ignore them
            time_2 = time.time()
            # If theres has been movement the last 1 sec mov on
            
            for contour in contours:
                #finds the coordinates of the countours
                (x,y,w,h) = cv2.boundingRect(contour)
                if (time_2 - time_1)>1: 
                    time_1 = time.time()
                    if cv2.contourArea(contour)>700:
                        message= "Movement"
                        self.mqtt_client.publish(MQTT_TOPIC_OUTPUT, message)
                        break
                # del for show rectangles
                #if cv2.contourArea(contour)>700:
                #    cv2.rectangle(frame1,(x,y),(x+w,y+h),(0,255,0),2)
                #    cv2.putText(frame1,"Status:{}".format('Movement'),(10,20),cv2.FONT_HERSHEY_SIMPLEX,
                #    1, (0,0,255),3)
                        
            #shows the picture
            cv2.imshow("webcam",frame1)
            frame1=frame2
            ret,frame2= cap.read()
    
            # press escape to exit
            if (cv2.waitKey(30) == 27):
                break
        cap.release()
        cv2.destroyAllWindows()

    

debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = SensorMovement()