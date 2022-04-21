# Temporary file for testing QR generator (should be removed later)
from datetime import datetime

from qr_generator import QrGenerator


def on_expired(found_qr):
    print("This link has expired: " + found_qr.get_link_id())


def on_found(found_qr):
    print("This link was found and valid: " + found_qr.get_link_id())


generator = QrGenerator(on_expired, on_found, "office2")
generator.generate_invite_link(datetime(2022, 4, 26))


while True:
    generator.loop()

