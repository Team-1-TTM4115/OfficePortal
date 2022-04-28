import datetime
import qrcode
import uuid


class InviteLink:
    """Invite Link with its own unique uuid, expirey date and an assosiated qr code """
    def __init__(self, expire):
        self.__link_id = str(uuid.uuid4())
        self.__expire = expire
        self.__qr_image = self.__link_id + '.png'

        img = qrcode.make(self.__link_id)
        img.save(self.__qr_image)

    def has_expired(self):
        """Checks if the current link has expired """
        time_now = datetime.datetime.now()
        return self.__expire <= time_now

    def get_link_id(self):
        return self.__link_id


