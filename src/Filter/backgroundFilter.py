import cv2
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import os
from pathlib import Path

webcam = cv2.VideoCapture(0)
webcam.set(3, 640)
webcam.set(4,480)

segmentor = SelfiSegmentation()
fpsReader = cvzone.FPS()

listImg = os.listdir(r"C:\Users\Bruker\Projects\OfficePortal\src\Filter\BackgroundFilters")
print(listImg)
imgList = []
for imgPath in listImg:
    path= 'C:/Users/Bruker/Projects/OfficePortal/src/Filter/BackgroundFilters/'
    imagePath= os.path.join(path, imgPath)
    img = cv2.imread(imagePath)
    imgList.append(img)

indexImg = 0
choice = 0
while True:
    size=4
    (rval, im) = webcam.read()
    im = cv2.flip(im, 1, 0)
    imgOut = segmentor.removeBG(im, imgList[indexImg], threshold=0.8)
    cv2.imshow("image", imgOut)

    key = cv2.waitKey(1)
    if key == ord('a'):
        if indexImg>0:
            indexImg -=1
    elif key == ord('b'):
        if indexImg<len(imgList)-1:
            indexImg +=1
    elif key == ord('q'):
        break


webcam.release()
cv2.destroyAllWindows()