from invite_link import InviteLink
from src.mqtt_client import MqttClient

TOPIC_CONNECT = 'ttm4115/team_1/project/connect'


class QrGenerator:
    def __init__(self, on_expired, on_found):
        """
        Class for generating qr code and listening if someone uses it
        :param on_expired: Callback for when an expired qr code is picked up with MQTT
        :param on_found: Callback for when a valid qr code is picked up with MQTT
        """
        self.__mqtt_client = MqttClient("Generator")
        self.__generated_links = []

        self.__mqtt_client.on_message = self.__on_message
        self.__mqtt_client.subscribe(TOPIC_CONNECT)

        self.__on_found = on_found
        self.__on_expired = on_expired

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
                self.__on_expired(found_qr)
            else:
                self.__on_found(found_qr)

    def start_loop(self):
        """ Starts listening to incoming messages """
        self.__mqtt_client.loop_start()

    def stop_loop(self):
        """ Stops listening to incoming messages """
        self.__mqtt_client.loop_stop()

    def loop(self):
        """ Used for manual loop (mostly when testing) """
        self.__mqtt_client.loop()
