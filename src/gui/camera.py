import cv2


def singleton(class_):
    """
    A singleton pattern to ensure that an object is only created once
    """
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class Camera(cv2.VideoCapture):
    """
    Camera using a singleton to prevent it from being created multiple times
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
