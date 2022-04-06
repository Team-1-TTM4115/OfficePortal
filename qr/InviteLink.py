import datetime
import qrcode
import uuid


class InviteLink:
    """Invite Link with its own unique id, expirey date and an assosiated qr code"""
    def __init__(self, expire):
        self.link_id = str(uuid.uuid1())
        self.expire = expire
        self.qr_image = self.link_id + '.png'

        img = qrcode.make(self.link_id)
        img.save(self.qr_image)

    def has_expired(self):
        """Checks if the current link has expired"""
        time_now = datetime.datetime.now()
        return self.expire <= time_now
