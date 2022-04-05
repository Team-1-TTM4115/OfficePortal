import datetime
import qrcode
import uuid


class InviteLink:
    def __init__(self, expire):
        self.link_id = uuid.uuid1()
        self.expire = expire
        self.qr_image = str(self.link_id) + '.png'

        img = qrcode.make(self.link_id)
        img.save(self.qr_image)

    def has_expired(self):
        time_now = datetime.datetime.now()
        return self.expire >= time_now
