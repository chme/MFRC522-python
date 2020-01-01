'''
Simpler interface compared to mfrc522.py to the NFC reader Module MFRC522 on the Raspberry Pi.
Inspired by https://github.com/pimylifeup/MFRC522-python

Copyright (c) 2019 Christian Meffert <christian.meffert@googlemail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import logging
import threading
import RPi.GPIO as GPIO
from .utils import (
    format_hex,
    FormatString as _F
)
from .mfrc522 import (
    MFRC522,
    PCD_Register,
    PICC_Command,
    StatusCode,
    PCD_Command,
    MIFARE_Key
)


logger_debug = logging.getLogger('mfrc522.log')


class SimpleMFRC522(object):
    '''
    '''

    def __init__(self, bus=0, device=0, speed=1000000, pin_reset=25, pin_ce=0, pin_irq=24, pin_mode=GPIO.BCM):
        '''
        Create a new SimpleMFRC522 instance

        @param bus: The SPI bus (default = 0)
        @param device: The SPI device (default = 0)
        @param speed: The max speed in Hz for the SPI device (default = 1000000)
        @param pin_reset: The GPIO reset pin number (default = 25)
        @param pin_ce: The GPIO chip select pin number (default = 0, not connected)
        @param pin_irq: The GPIO IRQ pin number (default = 24)
        @param pin_mode: GPIO pin numbering mode (default = GPIO.BCM)
        '''
        self.rfid = MFRC522(bus=bus, device=device, speed=speed, pin_reset=pin_reset,
                            pin_ce=pin_ce, pin_irq=pin_irq, pin_mode=pin_mode)
        self.irq = threading.Event()
        self.cancel_irq = threading.Event()

    def init(self):
        self.irq.clear()
        self.rfid.pcd_init()
        GPIO.add_event_detect(self.rfid.pin_irq, GPIO.FALLING,
                              callback=self.__interrupt_callback)

    def cleanup(self):
        self.rfid.pcd_cleanup()

    def is_new_card_present(self):
        return self.rfid.picc_is_new_card_present()

    def is_card_present(self):
        return self.rfid.picc_is_card_present()

    def read_card_serial(self):
        return self.rfid.picc_read_card_serial()

    def wait_for_interrupt(self):
        '''
        Blocks execution until an interrupt is detected (PICC found)
        Requires the interrupt GPIO pin to be connected.

        @return: True if cards is present, False if operation was canceled
        '''
        self.cancel_irq.clear()
        self.irq.clear()

        canceled = False
        try:
            logger_debug.debug('Waiting for interrupt from MFRC522')
            waiting = True
            while waiting and not canceled:
                # The receiving block needs regular retriggering (tell the tag
                # it should transmit??)
                self.__activate_reception()
                waiting = not self.irq.wait(0.1)
                canceled = self.cancel_irq.is_set()
            logger_debug.debug('Interrupt from MFRC522')
        finally:
            self.__clear_interrupt()
            self.cancel_irq.clear()
            self.irq.clear()

        return not canceled

    def __activate_reception(self):
        '''
        The function sending to the MFRC522 the needed commands to activate the reception
        '''
        # Allow the ... irq to be propagated to the IRQ pin
        # Propagate the IdleIrq and loAlert
        self.rfid.pcd_write_register(
            PCD_Register.ComIrqReg, 0x7F)  # clear interrupt
        #self.rfid.pcd_write_register(PCD_Register.ComIrqReg, 0x00)
        self.rfid.pcd_write_register(PCD_Register.ComIEnReg, 0xA0)  # rx irq

        self.rfid.pcd_write_register(
            PCD_Register.FIFODataReg, PICC_Command.PICC_CMD_REQA.value)
        self.rfid.pcd_write_register(
            PCD_Register.CommandReg, PCD_Command.PCD_Transceive.value)
        self.rfid.pcd_write_register(PCD_Register.BitFramingReg, 0x87)

    def __clear_interrupt(self):
        '''
        The function to clear the pending interrupt bits after interrupt serving routine
        '''
        self.rfid.pcd_write_register(PCD_Register.ComIrqReg, 0x7F)

    def __interrupt_callback(self, __):
        self.irq.set()

    def wait_for_card_removed(self, retries=5):
        '''
        Blocks until no cards are present (polls for new cards and if none are found in 5 times in a row 
        assumes that no card is present)

        @return: True if no cards are present, False if operation was canceled
        '''
        self.cancel_irq.clear()

        is_card_present = True
        canceled = False
        while is_card_present and not canceled:
            is_card_present = False
            # Assumes that if 5 consecutive requests fail, that no card is
            # present
            for __ in range(0, retries):
                if self.is_card_present():
                    is_card_present = True
            # Check if the operation should be canceled
            if is_card_present:
                canceled = self.cancel_irq.wait(0.5)

        self.cancel_irq.clear()
        return not canceled

    def cancel_wait(self):
        self.cancel_irq.set()

    def read_text(self, terminal_byte=0x00, encoding='UTF-8', errors='ignore'):
        '''
        Read all data blocks from a MIFARE Classic card until the given terminal byte (default is 0x00) is found and converts the data to 
        a string with the given encoding and error handling scheme (defaults to UTF-8 and error handling scheme 'ignore').
        In order to read all data blocks pass None as terminal_byte parameter.

        This method blocks until a MIFARE Classic card is present.

        @param terminal_byte: Byte value that indicates end of string (default = 0x00), set to None if all data should be returned
        @param encoding: The encoding used to decode the byte array into a string (default = 'UTF-8')
        @param errors: The error handling scheme if an decoding error occures (default = 'ignore', other possible values are 'strict' and 'replace')
        @return: (StatusCode, Uid, Text)
        '''

        status, uid, data = self.read_bytes(terminal_byte=terminal_byte)

        if not status:
            return status, uid, None

        byte_data = bytearray(data)
        return StatusCode.STATUS_OK, uid, byte_data.decode(encoding=encoding, errors=errors)

    def read_bytes(self, terminal_byte=0x00):
        '''
        Read all data blocks from a MIFARE Classic card until the given terminal byte (default is 0x00) is found.
        In order to read all data blocks pass None as terminal_byte parameter.

        This method blocks until a MIFARE Classic card is present.

        @param terminal_byte: Byte value that indicates end of data (default = 0x00), set to None if all data should be returned
        @return: (StatusCode, Uid, data)
        '''
        uid = None
        is_card_present = False
        while not is_card_present:
            canceled = not self.wait_for_interrupt()
            if canceled:
                return StatusCode.STATUS_CANCELED, None, None

            status, uid = self.rfid.picc_read_card_serial()
            if not status:
                logger_debug.warn(
                    _F('Failed to read UID in read_bytes (status: {}, uid: {})', status, uid))
                continue

            picc_type = uid.get_picc_type()
            if picc_type.is_mifare_classic():
                logger_debug.info(
                    _F('Card found: MIFARE Classic PICC (uid: {})', uid))
                is_card_present = True
            else:
                logger_debug.warn(
                    _F('Unsupported PICC type (type: {}, uid: {})', picc_type, uid))
                # Halt PICC
                self.rfid.picc_halt_a()

        status, data = self._read_mifare_classic(
            uid, terminal_byte=terminal_byte)

        # Halt PICC
        self.rfid.picc_halt_a()
        # Stop encryption on PCD
        self.rfid.pcd_stop_crypto1()

        if not status:
            return status, uid, None

        return status, uid, data

    def _read_mifare_classic(self, uid, terminal_byte=0x00):
        '''
        Read all data blocks from a previously selected MIFARE Classic card

        @param uid: UID from the selected PICC
        @param terminal_byte: Byte value that indicates end of data (default = 0x00), set to None if all data should be returned
        @return: (StatusCode, data) - data is a list of all bytes read from the data blocks of the selected PICC
        '''
        key = MIFARE_Key()
        picc_type = uid.get_picc_type()
        data = []
        for sector in range(0, picc_type.get_sector_count()):
            first_data_block, trailer_block, __ = picc_type.get_sector_definition(
                sector)

            # Authenticate using key A
            status = self.rfid.pcd_authenticate(
                PICC_Command.PICC_CMD_MF_AUTH_KEY_A, trailer_block, key, uid)
            if not status:
                logger_debug.error(
                    _F('Authentication failed (block_addr: {:#04x}, uid: [{}])', trailer_block, format_hex(uid.uid())))
                return status, None

            for block_addr in range(first_data_block, trailer_block):
                status, block_data = self.rfid.mifare_read(block_addr)
                if status != StatusCode.STATUS_OK:
                    logger_debug.error(
                        _F('Error reading from MIFARE Classic PICC (block_addr: {:#04x}, uid: [{}])', block_addr, format_hex(uid.uid())))
                    return status, None

                # A block contains exactly 16 bytes of data
                block_data = block_data[:16]
                # Terminal byte found, add the data up to the terminal byte and
                # return (stop reading following sectors/blocks
                if terminal_byte in block_data:
                    data += block_data[:block_data.index(terminal_byte)]
                    return StatusCode.STATUS_OK, data

                data += block_data

        return StatusCode.STATUS_OK, data

    def write_text(self, text, terminal_byte=0x00, encoding='UTF-8', errors='ignore'):
        '''
        Write given text to a MIFARE Classic card.
        The given terminal byte (default is 0x00) is appended as last data byte (pass None as parameter to not append any).
        Returns the old text stored on the PICC.

        This method blocks until a MIFARE Classic card is present, that can be written.

        @param text: The text to write to the PICC
        @param terminal_byte: Byte value that indicates end of data (default = 0x00), set to None if no terminal byte should be used
        @param encoding: The encoding used to decode the byte array into a string (default = 'UTF-8')
        @param errors: The error handling scheme if an decoding error occures (default = 'ignore', other possible values are 'strict' and 'replace')
        @return: (StatusCode, Uid, text)
        '''
        data = list(bytearray(text, encoding=encoding))
        status, uid, old_data = self.write_bytes(
            data, terminal_byte=terminal_byte)

        if not status:
            return status, uid, None

        old_byte_data = bytearray(old_data)
        return StatusCode.STATUS_OK, uid, old_byte_data.decode(encoding=encoding, errors=errors)

    def write_bytes(self, data, terminal_byte=0x00):
        '''
        Write given byte data list to a MIFARE Classic card.
        The given terminal byte (default is 0x00) is appended as last data byte (pass None as parameter to not append any).
        Returns the old data stored on the PICC.

        This method blocks until a MIFARE Classic card is present, that can be written.

        @param data: The list of bytes to to write to the PICC
        @param terminal_byte: Byte value that indicates end of data (default = 0x00), set to None if no terminal byte should be used
        @return: (StatusCode, Uid, text)
        '''
        # Wait for interrupt
        uid = None
        is_card_present = False
        while not is_card_present:
            canceled = not self.wait_for_interrupt()
            if canceled:
                return StatusCode.STATUS_CANCELED, None, None

            status, uid = self.rfid.picc_read_card_serial()
            if not status:
                logger_debug.warn(
                    _F('Failed to read UID in write_bytes (status: {}, uid: {})', status, uid))
                continue

            picc_type = uid.get_picc_type()
            if picc_type.is_mifare_classic():           # Only MIFARE Classic cards are supported for now
                logger_debug.info(
                    _F('Card found: MIFARE Classic PICC (uid: {})', uid))
                is_card_present = True
            else:
                logger_debug.warn(
                    _F('Unsupported PICC type (type: {}, uid: {})', picc_type, uid))
                # Halt PICC
                self.rfid.picc_halt_a()

        # Read old data from PICC
        status, old_data = self._read_mifare_classic(
            uid, terminal_byte=terminal_byte)

        # Write new data to PICC
        if status:
            status = self._write_mifare_classic(uid, data)

        # Halt PICC
        self.rfid.picc_halt_a()
        # Stop encryption on PCD
        self.rfid.pcd_stop_crypto1()

        return status, uid, old_data

    def _write_mifare_classic(self, uid, data, terminal_byte=0x00):
        '''
        Write data to a previously selected MIFARE Classic card

        @param uid: UID from the selected PICC
        @param data: The list of bytes to to write to the PICC
        @param terminal_byte: Byte value that indicates end of data (default = 0x00), set to None if no terminal byte should be used
        @return: StatusCode
        '''
        key = MIFARE_Key()
        picc_type = uid.get_picc_type()
        # Append terminal_byte if given
        all_data = data if not isinstance(
            terminal_byte, int) else data + [terminal_byte]
        all_block_data = [all_data[i:i + 16]
                          for i in range(0, len(all_data), 16)]
        data = []
        for sector in range(0, picc_type.get_sector_count()):
            first_data_block, trailer_block, __ = picc_type.get_sector_definition(
                sector)

            # Authenticate using key B
            status = self.rfid.pcd_authenticate(
                PICC_Command.PICC_CMD_MF_AUTH_KEY_B, trailer_block, key, uid)
            if not status:
                logger_debug.error(
                    _F('Authentication failed (block_addr: {:#04x}, uid: [{}])', trailer_block, format_hex(uid.uid())))
                return status, None

            for block_addr in range(first_data_block, trailer_block):
                block_data = all_block_data.pop(0)
                if len(block_data) < 16:
                    block_data += [0x00] * (16 - len(block_data))
                status = self.rfid.mifare_write(block_addr, block_data)
                if status != StatusCode.STATUS_OK:
                    logger_debug.error(
                        _F('Error writing to MIFARE Classic PICC (block_addr: {:#04x}, uid: [{}])', block_addr, format_hex(uid.uid())))
                    return status, uid, None

                if len(all_block_data) == 0:
                    return StatusCode.STATUS_OK

        if len(all_block_data) > 0:
            logger_debug.error(
                _F('To much data, could not write all data to MIFARE Classic PICC (uid: [{}])', format_hex(uid.uid())))

        return StatusCode.STATUS_OK
