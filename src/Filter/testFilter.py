import cv2

#face = cv2.CascadeClassifier('C:\Python310\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)
while True:
    ret, frame1 = cap.read()
    cv2.imshow("webcam",frame1)
     # press escape to exit
    if (cv2.waitKey(30) == 27):
        break
cap.release()
cv2.destroyAllWindows()