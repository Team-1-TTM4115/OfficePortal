from invite_link import InviteLink
from src.mqtt_client.mqtt_client import MqttClient

TOPIC_CONNECT = 'ttm4115/team_1/project/connect'


class QrGenerator:
    """ Class for generating qr code and listening if someone uses it """
    def __init__(self):
        self.__mqtt_client = MqttClient("Generator")
        self.__generated_links = []

        self.__mqtt_client.on_message = self.__on_message
        self.__mqtt_client.subscribe(TOPIC_CONNECT)

    def generate_invite_link(self, expire):
        """ Create a new QR code that can be used to connect """
        new_link = InviteLink(expire)
        self.__generated_links.append(new_link)
        return new_link

    def __on_message(self, client, userdata, message):
        link_id = str(message.payload.decode("utf-8"))
        found_qr = next((x for x in self.__generated_links if x.get_link_id() == link_id), None)
        if found_qr is not None:
            if found_qr.has_expired():
                print("Invite link \"" + found_qr.get_link_id() + "\" has expired")
                # TODO: Someone scanned an invalid QR code. What happens now?
            else:
                print("Connected")
                # TODO: Someone scanned a valid QR code. What happens now?

    def start_loop(self):
        """ Starts listening to incoming messages """
        self.__mqtt_client.loop_start()

    def stop_loop(self):
        """ Stops listening to incoming messages """
        self.__mqtt_client.loop_stop()

    def loop(self):
        """ Used for manual loop (mostly when testing) """
        self.__mqtt_client.loop()
