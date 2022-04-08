# Temporary file for testing QR generator (should be removed later)
from datetime import datetime

from qr_generator import QrGenerator

generator = QrGenerator()
generator.generate_invite_link(datetime(2022, 4, 26))

while True:
    generator.loop()

