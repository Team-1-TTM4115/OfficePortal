from src.gui.camera import Camera
import cv2

camera1 = Camera(0)
camera2 = Camera(0)


while True:
    ret, frame = camera1.read()
    ret2, frame2 = camera2.read()
    cv2.imshow("test1", frame)
    cv2.imshow("test2", frame2)
    if cv2.waitKey(1) & 0xFF == 27:
        break
camera1.release()
cv2.destroyAllWindows()

