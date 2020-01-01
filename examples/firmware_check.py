
import logging
import signal
import sys

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
    rfid.pcd_init()                             # Init MFRC522
    print('*****************************')
    print('MFRC522 Digital self test')
    print('*****************************')
    # Show details of PCD - MFRC522 Card Reader details
    rfid.pcd_dump_version_to_serial()
    print('-----------------------------')
    print('Only known versions supported')
    print('-----------------------------')
    print('Performing test...')
    result = rfid.pcd_perform_self_test()       # perform the test
    print('-----------------------------')
    print('Result: {}'.format('OK' if result else 'DEFECT or UNKNOWN'))


rfid = MFRC522()
try:
    setup(rfid)

finally:
    rfid.pcd_cleanup()
