
import logging
import signal
import sys

from time import sleep
from mfrc522 import MFRC522, PICC_Type, PICC_Command, MIFARE_Key, StatusCode, format_hex


logging.basicConfig(level=logging.INFO)
run = True


def end(signal, frame):
    global run
    print('Ctrl+C captured, ending example program.')
    run = False
    sys.exit()


signal.signal(signal.SIGINT, end)


def setup(rfid, key):
    rfid.pcd_init()                     # Init MFRC522
    # Show details of PCD - MFRC522 Card Reader details
    rfid.pcd_dump_version_to_serial()
    print('Scan a MIFARE Classic PICC to demonstrate read and write.')
    print('Using key (for A and B): {}'.format(format_hex(key.key_byte)))
    print()
    print('BEWARE: Data will be written to the PICC, in sector #1')


def loop(rfid, key):
    # Look for new cards
    if not rfid.picc_is_new_card_present():
        return

    # Select one of the cards
    result, uid = rfid.picc_read_card_serial()
    if not result:
        return

    print()

    # Show some details of the PICC (that is: the tag/card)
    rfid.picc_dump_details_to_serial(uid)

    # Check for compatibility
    picc_type = uid.get_picc_type()
    if (picc_type != PICC_Type.PICC_TYPE_MIFARE_MINI
            and picc_type != PICC_Type.PICC_TYPE_MIFARE_1K
            and picc_type != picc_type != PICC_Type.PICC_TYPE_MIFARE_4K):
        print('This sample only works with MIFARE Classic cards.')
        return

    # In this sample we use the second sector,
    # that is: sector #1, covering block #4 up to and including block #7
    sector = 1
    block_addr = 4
    data_block = [
        0x01, 0x02, 0x03, 0x04,  # 1,  2,  3,   4,
        0x05, 0x06, 0x07, 0x08,  # 5,  6,  7,   8,
        0x09, 0x0a, 0xff, 0x0b,  # 9,  10, 255, 11,
        0x0c, 0x0d, 0x0e, 0x0f   # 12, 13, 14,  15
    ]
    trailer_block = 7

    # Authenticate using key A
    print('Authenticating using key A...')
    status = rfid.pcd_authenticate(
        PICC_Command.PICC_CMD_MF_AUTH_KEY_A, trailer_block, key, uid)
    if status != StatusCode.STATUS_OK:
        print('PCD_Authenticate() failed: {}'.format(status))
        return

    # Show the whole sector as it currently is
    print('Current data in sector: ')
    rfid.picc_dump_mifare_classic_sector_to_serial(uid, key, sector)
    print()

    # Read data from the block
    print('Reading data from block {:#04x} ...'.format(block_addr))
    status, data = rfid.mifare_read(block_addr)
    if status != StatusCode.STATUS_OK:
        print('MIFARE_Read() failed: {}'.format(status))

    print('Data in block {}: [{}]'.format(block_addr, format_hex(data[:16])))
    print()

    # Authenticate using key B
    print('Authenticating again using key B...')
    status = rfid.pcd_authenticate(
        PICC_Command.PICC_CMD_MF_AUTH_KEY_B, trailer_block, key, uid)
    if status != StatusCode.STATUS_OK:
        print('PCD_Authenticate() failed: {}'.format(status))
        return

    # Write data to the block
    print('Writing data into block {:#04x} ...'.format(block_addr))
    print('Data: [{}]'.format(format_hex(data_block)))
    status = rfid.mifare_write(block_addr, data_block)
    if status != StatusCode.STATUS_OK:
        print('MIFARE_Write() failed: {}'.format(status))
    print()

    # Read data from the block (again, should now be what we have written)
    print('Reading data from block {:#04x} ...'.format(block_addr))
    status, data = rfid.mifare_read(block_addr)
    if status != StatusCode.STATUS_OK:
        print('MIFARE_Read() failed: {}'.format(status))

    print('Data in block {}: [{}]'.format(block_addr, format_hex(data[:16])))
    print()

    # Check that data in block is what we have written
    # by counting the number of bytes that are equal
    print('Checking result...')
    count = 0
    for i in range(16):
        # Compare buffer (= what we've read) with dataBlock (= what we've
        # written)
        if data[i] == data_block[i]:
            count += 1
    print('Number of bytes that match = {}'.format(count))
    if count == 16:
        print('Success :-)')
    else:
        print('Failure, no match :-(')
        print('  perhaps the write did not work properly...')
    print()

    # Dump the sector data
    print('Current data in sector:')
    rfid.picc_dump_mifare_classic_sector_to_serial(uid, key, sector)
    print()

    # Halt PICC
    rfid.picc_halt_a()
    # Stop encryption on PCD
    rfid.pcd_stop_crypto1()


rfid = MFRC522()

# Prepare the key (used both as key A and as key B)
# using FFFFFFFFFFFFh which is the default at chip delivery from the factory
key = MIFARE_Key()

try:
    setup(rfid, key)
    while run:
        print('.', end='')
        loop(rfid, key)
        sleep(1)

finally:
    rfid.pcd_cleanup()
