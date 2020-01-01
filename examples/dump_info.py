
import logging
import signal
import sys

from time import sleep
from mfrc522 import MFRC522


logging.basicConfig(level=logging.INFO)
run = True


def end(signal, frame):
    global run
    print('Ctrl+C captured, ending example program.')
    run = False
    sys.exit()


signal.signal(signal.SIGINT, end)


def setup(rfid):
    rfid.pcd_init()                     # Init MFRC522
    # Show details of PCD - MFRC522 Card Reader details
    rfid.pcd_dump_version_to_serial()
    print('Scan PICC to see UID, SAK, type, and data blocks...')
    print('(Press CTRL+C to quit)')


def loop(rfid):
    # Look for new cards
    if not rfid.picc_is_new_card_present():
        return

    # Select one of the cards
    result, uid = rfid.picc_read_card_serial()
    if not result:
        return

    # Dump debug info about the card; PICC_HaltA() is automatically called
    print()
    print('New PICC')
    rfid.picc_dump_to_serial(uid)
    print()


rfid = MFRC522()
try:
    setup(rfid)
    while run:
        print('.', end='')
        loop(rfid)
        sleep(1)

finally:
    rfid.pcd_cleanup()
