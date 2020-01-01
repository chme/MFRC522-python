
import logging
import signal
import sys

from time import sleep
from mfrc522 import MFRC522, PCD_Register, PCD_Command, PICC_Command
import RPi.GPIO as GPIO


logging.basicConfig(level=logging.INFO)
run = True


def end(signal, frame):
    global run
    print('Ctrl+C captured, ending example program.')
    run = False
    sys.exit()


signal.signal(signal.SIGINT, end)


b_new_int = False


def read_card(pin):
    '''
    MFRC522 interrupt serving routine
    '''
    global b_new_int
    b_new_int = True


def activate_rec(rfid):
    '''
    The function sending to the MFRC522 the needed commands to activate the reception
    '''
    rfid.pcd_write_register(PCD_Register.FIFODataReg,
                            PICC_Command.PICC_CMD_REQA.value)
    rfid.pcd_write_register(PCD_Register.CommandReg,
                            PCD_Command.PCD_Transceive.value)
    rfid.pcd_write_register(PCD_Register.BitFramingReg, 0x87)


def clear_int(rfid):
    '''
    The function to clear the pending interrupt bits after interrupt serving routine
    '''
    rfid.pcd_write_register(PCD_Register.ComIrqReg, 0x7F)


def setup(rfid):
    rfid.pcd_init()                     # Init MFRC522
    # Show details of PCD - MFRC522 Card Reader details
    rfid.pcd_dump_version_to_serial()
    print('Scan PICC to see UID...')
    print('(Press CTRL+C to quit)')

    # Allow the ... irq to be propagated to the IRQ pin
    # For test purposes propagate the IdleIrq and loAlert
    reg_val = 0xA0  # rx irq
    rfid.pcd_write_register(PCD_Register.ComIEnReg, reg_val)

    # Activate the interrupt
    GPIO.add_event_detect(rfid.pin_irq, GPIO.FALLING, callback=read_card)

    print('End setup')


def loop(rfid):
    global b_new_int
    if b_new_int:   # new read interrupt
        print()
        print('Interrupt')
        # Select one of the cards
        result, uid = rfid.picc_read_card_serial()
        if not result:
            return
        print('Card UID: {}'.format(uid))
        rfid.picc_halt_a()
        print()
        clear_int(rfid)
        b_new_int = False

    # The receiving block needs regular retriggering (tell the tag it should transmit??)
    # (mfrc522.PCD_WriteRegister(mfrc522.FIFODataReg,mfrc522.PICC_CMD_REQA);)
    activate_rec(rfid)


rfid = MFRC522()
try:
    setup(rfid)
    while run:
        print('.', end='')
        loop(rfid)
        sleep(0.1)

finally:
    rfid.pcd_cleanup()
