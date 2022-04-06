import datetime
import time

from InviteLink import InviteLink
from MqttClient import MqttClient

TOPIC_CONNECT = 'ttm4115/team_1/project/connect'

mqtt_client = MqttClient("1")
all_links = []


def generate_invite_link(expire):
    all_links.append(InviteLink(expire))


def on_message(client, userdata, message):
    link_id = str(message.payload.decode("utf-8"))
    found_qr = next((x for x in all_links if x.link_id == link_id), None)
    if found_qr is not None:
        if found_qr.has_expired():
            print("Invite link \"" + found_qr.link_id + "\" has expired")
        else:
            print("Connected")
            # Do stuff here


generate_invite_link(datetime.datetime(2022, 4, 26))
mqtt_client.client.on_message = on_message
mqtt_client.client.subscribe(TOPIC_CONNECT)
while True:
    mqtt_client.client.loop()
