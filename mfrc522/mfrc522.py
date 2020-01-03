'''
Library to interface with the NFC reader Module MFRC522 on the Raspberry Pi. 
This is a Python port of the "Arduino RFID Library for MFRC522" published by
under the public domain (https://github.com/miguelbalboa/rfid).

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

'''
Python port of the "Arduino RFID Library for MFRC522" from 2019-01-16 (https://github.com/miguelbalboa/rfid).
An earlier port of the same library can be found at https://github.com/mxgxw/MFRC522-python.

There is a lot of documentation available at https://github.com/miguelbalboa/rfid with useful hints and background information.
I tried to preserve all code comments from the original source. The source code resembles the logic of the Arduino version
to be able to port future changes without to much hassle (that means the implementation might not be the best python example).

IMPORTANT: This is still work in progress and greatly untested! Use at own risk!


The following loggers are used enumerated by names:

- 'mfrc522.log':     Log errors and warnings
- 'mfrc522.trace':   Log to method calls and steps (verbose)
- 'mfrc522.spi':     Log SPI communication (very verbose)

You may subscribe to these loggers for getting logging messages.


#====================================================================================
# Documentation from MFRC522.h (https://github.com/miguelbalboa/rfid)
#====================================================================================

MFRC522.h - Library to use ARDUINO RFID MODULE KIT 13.56 MHZ WITH TAGS SPI W AND R BY COOQROBOT.
Based on code Dr.Leong   ( WWW.B2CQSHOP.COM )
Created by Miguel Balboa (circuitito.com), Jan, 2012.
Rewritten by Søren Thing Andersen (access.thing.dk), fall of 2013 (Translation to English, refactored, comments, anti collision, cascade levels.)
Extended by Tom Clement with functionality to write to sector 0 of UID changeable Mifare cards.
Released into the public domain.

Please read this file for an overview and then MFRC522.cpp for comments on the specific functions.
Search for "mf-rc522" on ebay.com to purchase the MF-RC522 board. 

There are three hardware components involved:
1) The micro controller: An Arduino
2) The PCD (short for Proximity Coupling Device): NXP MFRC522 Contactless Reader IC
3) The PICC (short for Proximity Integrated Circuit Card): A card or tag using the ISO 14443A interface, eg Mifare or NTAG203.

The microcontroller and card reader uses SPI for communication.
The protocol is described in the MFRC522 datasheet: http://www.nxp.com/documents/data_sheet/MFRC522.pdf

The card reader and the tags communicate using a 13.56MHz electromagnetic field.
The protocol is defined in ISO/IEC 14443-3 Identification cards -- Contactless integrated circuit cards -- Proximity cards -- Part 3: Initialization and anticollision".
A free version of the final draft can be found at http://wg8.de/wg8n1496_17n3613_Ballot_FCD14443-3.pdf
Details are found in chapter 6, Type A – Initialization and anticollision.

If only the PICC UID is wanted, the above documents has all the needed information.
To read and write from MIFARE PICCs, the MIFARE protocol is used after the PICC has been selected.
The MIFARE Classic chips and protocol is described in the datasheets:
       1K:   http://www.mouser.com/ds/2/302/MF1S503x-89574.pdf
        4K:   http://datasheet.octopart.com/MF1S7035DA4,118-NXP-Semiconductors-datasheet-11046188.pdf
        Mini: http://www.idcardmarket.com/download/mifare_S20_datasheet.pdf
The MIFARE Ultralight chip and protocol is described in the datasheets:
       Ultralight:   http://www.nxp.com/documents/data_sheet/MF0ICU1.pdf
        Ultralight C: http://www.nxp.com/documents/short_data_sheet/MF0ICU2_SDS.pdf

MIFARE Classic 1K (MF1S503x):
        Has 16 sectors * 4 blocks/sector * 16 bytes/block = 1024 bytes.
        The blocks are numbered 0-63.
        Block 3 in each sector is the Sector Trailer. See http://www.mouser.com/ds/2/302/MF1S503x-89574.pdf sections 8.6 and 8.7:
                Bytes 0-5:   Key A
                Bytes 6-8:   Access Bits
                Bytes 9:     User data
                Bytes 10-15: Key B (or user data)
        Block 0 is read-only manufacturer data.
        To access a block, an authentication using a key from the block's sector must be performed first.
        Example: To read from block 10, first authenticate using a key from sector 3 (blocks 8-11).
        All keys are set to FFFFFFFFFFFFh at chip delivery.
        Warning: Please read section 8.7 "Memory Access". It includes this text: if the PICC detects a format violation the whole sector is irreversibly blocked.
       To use a block in "value block" mode (for Increment/Decrement operations) you need to change the sector trailer. Use PICC_SetAccessBits() to calculate the bit patterns.
MIFARE Classic 4K (MF1S703x):
        Has (32 sectors * 4 blocks/sector + 8 sectors * 16 blocks/sector) * 16 bytes/block = 4096 bytes.
        The blocks are numbered 0-255.
        The last block in each sector is the Sector Trailer like above.
MIFARE Classic Mini (MF1 IC S20):
        Has 5 sectors * 4 blocks/sector * 16 bytes/block = 320 bytes.
        The blocks are numbered 0-19.
        The last block in each sector is the Sector Trailer like above.

MIFARE Ultralight (MF0ICU1):
        Has 16 pages of 4 bytes = 64 bytes.
        Pages 0 + 1 is used for the 7-byte UID.
        Page 2 contains the last check digit for the UID, one byte manufacturer internal data, and the lock bytes (see http://www.nxp.com/documents/data_sheet/MF0ICU1.pdf section 8.5.2)
        Page 3 is OTP, One Time Programmable bits. Once set to 1 they cannot revert to 0.
        Pages 4-15 are read/write unless blocked by the lock bytes in page 2. 
MIFARE Ultralight C (MF0ICU2):
        Has 48 pages of 4 bytes = 192 bytes.
        Pages 0 + 1 is used for the 7-byte UID.
        Page 2 contains the last check digit for the UID, one byte manufacturer internal data, and the lock bytes (see http://www.nxp.com/documents/data_sheet/MF0ICU1.pdf section 8.5.2)
        Page 3 is OTP, One Time Programmable bits. Once set to 1 they cannot revert to 0.
        Pages 4-39 are read/write unless blocked by the lock bytes in page 2. 
        Page 40 Lock bytes
        Page 41 16 bit one way counter
        Pages 42-43 Authentication configuration
        Pages 44-47 Authentication key 
'''

import logging
from time import sleep

import RPi.GPIO as GPIO
from enum import Enum
import spidev

from .utils import format_hex
from .utils import FormatString as _F


logger_debug = logging.getLogger('mfrc522.log')
logger_trace = logging.getLogger('mfrc522.trace')
logger_spi = logging.getLogger('mfrc522.spi')


#=========================================================================
# Enum definitions
#=========================================================================


class ValueDescriptionEnum(Enum):
    def __new__(cls, value,  description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj


class PCD_Register(ValueDescriptionEnum):
    '''
    MFRC522 registers. Described in chapter 9 of the datasheet.
    When using SPI all addresses are shifted one bit left in the "SPI address byte" (section 8.1.2.3)
    '''

    # Page 0: Command and status
    _Reserved_0x00 = (0x00 << 1, 'reserved for future use')
    CommandReg = (0x01 << 1, 'starts and stops command execution')
    ComIEnReg = (
        0x02 << 1, 'enable and disable interrupt request control bits')
    DivIEnReg = (
        0x03 << 1, 'enable and disable interrupt request control bits')
    ComIrqReg = (0x04 << 1, 'interrupt request bits')
    DivIrqReg = (0x05 << 1, 'interrupt request bits')
    ErrorReg = (
        0x06 << 1, 'error bits showing the error status of the last command executed')
    Status1Reg = (0x07 << 1, 'communication status bits')
    Status2Reg = (0x08 << 1, 'receiver and transmitter status bits')
    FIFODataReg = (0x09 << 1, 'input and output of 64 byte FIFO buffer')
    FIFOLevelReg = (0x0A << 1, 'number of bytes stored in the FIFO buffer')
    WaterLevelReg = (
        0x0B << 1, 'level for FIFO underflow and overflow warning')
    ControlReg = (0x0C << 1, 'miscellaneous control registers')
    BitFramingReg = (0x0D << 1, 'adjustments for bit-oriented frames')
    CollReg = (
        0x0E << 1, 'bit position of the first bit-collision detected on the RF interface')
    _Rserved_0x0F = (0x0F << 1, 'reserved for future use')

    # Page 1: Command
    _Reserved_0x10 = (0x10, 'reserved for future use')
    ModeReg = (0x11 << 1, 'defines general modes for transmitting and receiving ')
    TxModeReg = (0x12 << 1, 'defines transmission data rate and framing')
    RxModeReg = (0x13 << 1, 'defines reception data rate and framing')
    TxControlReg = (
        0x14 << 1, 'controls the logical behavior of the antenna driver pins TX1 and TX2')
    TxASKReg = (0x15 << 1, 'controls the setting of the transmission modulation')
    TxSelReg = (0x16 << 1, 'selects the internal sources for the antenna driver')
    RxSelReg = (0x17 << 1, 'selects internal receiver settings')
    RxThresholdReg = (0x18 << 1, 'selects thresholds for the bit decoder')
    DemodReg = (0x19 << 1, 'defines demodulator settings')
    _Reserved_0x1A = (0x1A, 'reserved for future use')
    _Reserved_0x1B = (0x1B, 'reserved for future use')
    MfTxReg = (0x1C << 1, 'controls some MIFARE communication transmit parameters')
    MfRxReg = (0x1D << 1, 'controls some MIFARE communication receive parameters')
    _Reserved_0x1E = (0x1E, 'reserved for future use')
    SerialSpeedReg = (
        0x1F << 1, 'selects the speed of the serial UART interface')

    # Page 2: Configuration
    _Reserved_0x20 = (0x20, 'reserved for future use')
    CRCResultRegH = (
        0x21 << 1, 'shows the MSB and LSB values of the CRC calculation')
    CRCResultRegL = (
        0x22 << 1, 'shows the MSB and LSB values of the CRC calculation')
    _Reserved_0x23 = (0x23, 'reserved for future use')
    ModWidthReg = (0x24 << 1, 'controls the ModWidth setting?')
    _Reserved_0x25 = (0x25, 'reserved for future use')
    RFCfgReg = (0x26 << 1, 'configures the receiver gain')
    GsNReg = (
        0x27 << 1, 'selects the conductance of the antenna driver pins TX1 and TX2 for modulation')
    CWGsPReg = (
        0x28 << 1, 'defines the conductance of the p-driver output during periods of no modulation')
    ModGsPReg = (
        0x29 << 1, 'defines the conductance of the p-driver output during periods of modulation')
    TModeReg = (0x2A << 1, 'defines settings for the internal timer')
    TPrescalerReg = (
        0x2B << 1, 'the lower 8 bits of the TPrescaler value. The 4 high bits are in TModeReg.')
    TReloadRegH = (0x2C << 1, 'defines the 16-bit timer reload value')
    TReloadRegL = (0x2D << 1, 'defines the 16-bit timer reload value')
    TCounterValueRegH = (0x2E << 1, 'shows the 16-bit timer value')
    TCounterValueRegL = (0x2F << 1, 'shows the 16-bit timer value')

    # Page 3: Test Registers
    _Reserved_0x30 = (0x30, 'reserved for future use')
    TestSel1Reg = (0x31 << 1, 'general test signal configuration')
    TestSel2Reg = (0x32 << 1, 'general test signal configuration')
    TestPinEnReg = (0x33 << 1, 'enables pin output driver on pins D1 to D7')
    TestPinValueReg = (
        0x34 << 1, 'defines the values for D1 to D7 when it is used as an I/O bus')
    TestBusReg = (0x35 << 1, 'shows the status of the internal test bus')
    AutoTestReg = (0x36 << 1, 'controls the digital self-test')
    VersionReg = (0x37 << 1, 'shows the software version')
    AnalogTestReg = (0x38 << 1, 'controls the pins AUX1 and AUX2')
    TestDAC1Reg = (0x39 << 1, 'defines the test value for TestDAC1')
    TestDAC2Reg = (0x3A << 1, 'defines the test value for TestDAC2')
    TestADCReg = (0x3B << 1, 'shows the value of ADC I and Q channels')
    _Reserved_0x3C = (0x3C, 'reserved for production tests')
    _Reserved_0x3D = (0x3D, 'reserved for production tests')
    _Reserved_0x3E = (0x3E, 'reserved for production tests')
    _Reserved_0x3F = (0x3F, 'reserved for production tests')


class PCD_Command(ValueDescriptionEnum):
    '''
    MFRC522 commands. Described in chapter 10 of the datasheet.
    '''
    PCD_Idle = (0x00, 'no action, cancels current command execution')
    PCD_Mem = (0x01, 'stores 25 bytes into the internal buffer')
    PCD_GenerateRandomID = (0x02, 'generates a 10-byte random ID number')
    PCD_CalcCRC = (
        0x03, 'activates the CRC coprocessor or performs a self-test')
    PCD_Transmit = (0x04, 'transmits data from the FIFO buffer')
    PCD_NoCmdChange = (
        0x07, 'no command change, can be used to modify the CommandReg register bits without affecting the command, for example, the PowerDown bit')
    PCD_Receive = (0x08, 'activates the receiver circuits')
    PCD_Transceive = (
        0x0C, 'transmits data from FIFO buffer to antenna and automatically activates the receiver after transmission')
    PCD_MFAuthent = (
        0x0E, 'performs the MIFARE standard authentication as a reader')
    PCD_SoftReset = (0x0F, 'resets the MFRC522')


class PCD_RxGain(ValueDescriptionEnum):
    '''
    MFRC522 RxGain[2:0] masks, defines the receiver's signal voltage gain factor (on the PCD).
    Described in 9.3.3.6 / table 98 of the datasheet at http://www.nxp.com/documents/data_sheet/MFRC522.pdf
    '''
    RxGain_18dB = (0x00 << 4, '000b - 18 dB, minimum')
    RxGain_23dB = (0x01 << 4, '001b - 23 dB')
    RxGain_18dB_2 = (
        0x02 << 4, '010b - 18 dB, it seems 010b is a duplicate for 000b')
    RxGain_23dB_2 = (
        0x03 << 4, '011b - 23 dB, it seems 011b is a duplicate for 001b')
    RxGain_33dB = (0x04 << 4, '100b - 33 dB, average, and typical default')
    RxGain_38dB = (0x05 << 4, '101b - 38 dB')
    RxGain_43dB = (0x06 << 4, '110b - 43 dB')
    RxGain_48dB = (0x07 << 4, '111b - 48 dB, maximum')
    RxGain_min = (
        0x00 << 4, '000b - 18 dB, minimum, convenience for RxGain_18dB')
    RxGain_avg = (
        0x04 << 4, '100b - 33 dB, average, convenience for RxGain_33dB')
    RxGain_max = (
        0x07 << 4, '111b - 48 dB, maximum, convenience for RxGain_48dB')


class PICC_Command(ValueDescriptionEnum):
    '''
    Commands sent to the PICC.
    '''
    # The commands used by the PCD to manage communication with several PICCs
    # (ISO 14443-3, Type A, section 6.4)
    PICC_CMD_REQA = (
        0x26, 'REQuest command, Type A. Invites PICCs in state IDLE to go to READY and prepare for anticollision or selection. 7 bit frame.')
    PICC_CMD_WUPA = (
        0x52, 'Wake-UP command, Type A. Invites PICCs in state IDLE and HALT to go to READY(*) and prepare for anticollision or selection. 7 bit frame.')
    PICC_CMD_CT = (
        0x88, 'Cascade Tag. Not really a command, but used during anti collision.')
    PICC_CMD_SEL_CL1 = (0x93, 'Anti collision/Select, Cascade Level 1')
    PICC_CMD_SEL_CL2 = (0x95, 'Anti collision/Select, Cascade Level 2')
    PICC_CMD_SEL_CL3 = (0x97, 'Anti collision/Select, Cascade Level 3')
    PICC_CMD_HLTA = (
        0x50, 'HaLT command, Type A. Instructs an ACTIVE PICC to go to state HALT.')
    PICC_CMD_RATS = (0xE0, 'Request command for Answer To Reset.')

    # The commands used for MIFARE Classic (from http://www.mouser.com/ds/2/302/MF1S503x-89574.pdf, Section 9)
    # Use PCD_MFAuthent to authenticate access to a sector, then use these commands to read/write/modify the blocks on the sector.
    # The read/write commands can also be used for MIFARE Ultralight.
    PICC_CMD_MF_AUTH_KEY_A = (0x60, 'Perform authentication with Key A')
    PICC_CMD_MF_AUTH_KEY_B = (0x61, 'Perform authentication with Key B')
    PICC_CMD_MF_READ = (
        0x30, 'Reads one 16 byte block from the authenticated sector of the PICC. Also used for MIFARE Ultralight.')
    PICC_CMD_MF_WRITE = (
        0xA0, 'Writes one 16 byte block to the authenticated sector of the PICC. Called "COMPATIBILITY WRITE" for MIFARE Ultralight.')
    PICC_CMD_MF_DECREMENT = (
        0xC0, 'Decrements the contents of a block and stores the result in the internal data register.')
    PICC_CMD_MF_INCREMENT = (
        0xC1, 'Increments the contents of a block and stores the result in the internal data register.')
    PICC_CMD_MF_RESTORE = (
        0xC2, 'Reads the contents of a block into the internal data register.')
    PICC_CMD_MF_TRANSFER = (
        0xB0, 'Writes the contents of the internal data register to a block.')

    # The commands used for MIFARE Ultralight (from http://www.nxp.com/documents/data_sheet/MF0ICU1.pdf, Section 8.6)
    # The PICC_CMD_MF_READ and PICC_CMD_MF_WRITE can also be used for MIFARE
    # Ultralight.
    PICC_CMD_UL_WRITE = (0xA2, 'Writes one 4 byte page to the PICC.')


class MIFARE_Misc(ValueDescriptionEnum):
    '''
    MIFARE constants that does not fit anywhere else
    '''
    MF_ACK = (
        0xA, 'The MIFARE Classic uses a 4 bit ACK/NAK. Any other value than 0xA is NAK.')
    MF_KEY_SIZE = (6, 'A Mifare Crypto1 key is 6 bytes.')


class PICC_Type(ValueDescriptionEnum):
    '''
    PICC types we can detect. Remember to update PICC_GetTypeName() if you add more.
    '''
    PICC_TYPE_UNKNOWN = (-1, 'Unknown PICC type')
    PICC_TYPE_ISO_14443_4 = (0x20, 'PICC compliant with ISO/IEC 14443-4')
    PICC_TYPE_ISO_18092 = (0x40, 'PICC compliant with ISO/IEC 18092 (NFC)')
    PICC_TYPE_MIFARE_MINI = (0x09, 'MIFARE Classic protocol, 320 bytes')
    PICC_TYPE_MIFARE_1K = (0x08, 'MIFARE Classic protocol, 1KB')
    PICC_TYPE_MIFARE_4K = (0x18, 'MIFARE Classic protocol, 4KB')
    PICC_TYPE_MIFARE_UL = (0x00, 'MIFARE Ultralight or Ultralight C')
    PICC_TYPE_MIFARE_PLUS = (0x10, 'MIFARE Plus')
    PICC_TYPE_MIFARE_DESFIRE = (0x11, 'MIFARE DESFire')
    PICC_TYPE_TNP3XXX = (
        0x01, 'Only mentioned in NXP AN 10833 MIFARE Type Identification Procedure')
    PICC_TYPE_NOT_COMPLETE = (0x04, 'SAK indicates UID is not complete.')

    def get_name(self):
        '''
        Returns the PICC type name.

        @return: PICC type name
        '''
        return self.description

    def is_mifare_classic(self):
        return (self == PICC_Type.PICC_TYPE_MIFARE_MINI
                or self == PICC_Type.PICC_TYPE_MIFARE_1K
                or self == PICC_Type.PICC_TYPE_MIFARE_4K)

    def is_mifare_ultrlight(self):
        return self == PICC_Type.PICC_TYPE_MIFARE_UL

    def get_sector_count(self):
        if self == PICC_Type.PICC_TYPE_MIFARE_MINI:
            # Has 5 sectors * 4 blocks/sector * 16 bytes/block = 320 bytes.
            no_of_sectors = 5
        elif self == PICC_Type.PICC_TYPE_MIFARE_1K:
            # Has 16 sectors * 4 blocks/sector * 16 bytes/block = 1024 bytes.
            no_of_sectors = 16
        elif self == PICC_Type.PICC_TYPE_MIFARE_4K:
            # Has (32 sectors * 4 blocks/sector + 8 sectors * 16 blocks/sector)
            # * 16 bytes/block = 4096 bytes.
            no_of_sectors = 40
        else:
            no_of_sectors = 0
        return no_of_sectors

    def get_sector_definition(self, sector):
        '''
        Returns the trailer block address, the block address for the first data block and the data block count
        for the given sector.

        @param sector: The sector number
        @return: (irst data block, sector trailer block, fdata block count)
        '''
        sector_trailer_block_addr = 0
        first_data_block_addr = 0
        data_block_count = 0

        if sector == 0:                             # Sector 0 has 4 blocks, but only 3 data blocks, the first block contains manufacturer data
            no_of_blocks = 4
            data_block_count = 2
            first_data_block_addr = 1
            sector_trailer_block_addr = 3
        elif sector < 32:                           # Sectors 0..31 has 4 blocks each
            no_of_blocks = 4
            data_block_count = 3
            first_data_block_addr = sector * no_of_blocks
            sector_trailer_block_addr = first_data_block_addr + 3
        elif sector < 40:                           # Sectors 32-39 has 16 blocks each
            no_of_blocks = 16
            data_block_count = 15
            first_data_block_addr = 128 + (sector - 32) * no_of_blocks
            sector_trailer_block_addr = first_data_block_addr + 15

        return first_data_block_addr, sector_trailer_block_addr, data_block_count

    def get_max_data_bytes(self):
        # 3 data block per sector and only 2 data blocks for sector 0
        no_of_data_blocks = (self.get_sector_count() * 3) - 1
        return no_of_data_blocks * 16                           # 16 bytes per block

    def __str__(self):
        return self.get_name() + ' ' + Enum.__str__(self)


class StatusCode(ValueDescriptionEnum):
    '''
    Return codes from the functions in this class. Remember to update GetStatusCodeName() if you add more.
    '''

    STATUS_OK = (0, 'Success')
    STATUS_ERROR = (1, 'Error in communication')
    STATUS_COLLISION = (2, 'Collission detected')
    STATUS_TIMEOUT = (3, 'Timeout in communication.')
    STATUS_NO_ROOM = (4, 'A buffer is not big enough.')
    STATUS_INTERNAL_ERROR = (
        5, 'Internal error in the code. Should not happen ;-)')
    STATUS_INVALID = (6, 'Invalid argument.')
    STATUS_CRC_WRONG = (7, 'The CRC_A does not match')
    STATUS_MIFARE_NACK = (8, 'A MIFARE PICC responded with NAK.')
    STATUS_CANCELED = (
        9, 'Used in SimpleMFRC522 to signal that blocking read/write was canceled')

    def get_name(self):
        '''
        Returns the status code name.

        @return:  StatusCode name
        '''
        return self.description

    def __bool__(self):
        return self == StatusCode.STATUS_OK

    def __str__(self):
        return self.description + ' ' + Enum.__str__(self)


#=========================================================================
# UID and MIFARE KEY classes
#=========================================================================


class Uid(object):
    '''
    A struct used for passing the UID of a PICC.
    '''
    # Number of bytes in the UID. 4, 7 or 10
    size = 0
    uid_byte = [0] * 10
    # The SAK (Select acknowledge) byte returned from the PICC after
    # successful selection.
    sak = None

    def uid(self):
        return self.uid_byte[:self.size]

    def to_num(self):
        n = 0
        uid = self.uid()
        for i in range(0, len(uid)):
            n = n * 256 + uid[i]
        return n

    def get_picc_type(self):
        '''
        Translates the SAK (Select Acknowledge) to a PICC type.

        @param sak: The SAK byte returned from PICC_Select().
        @return: PICC_Type
        '''
        picc_type = PICC_Type.PICC_TYPE_UNKNOWN

        # http://www.nxp.com/documents/application_note/AN10833.pdf
        # 3.2 Coding of Select Acknowledge (SAK)
        # ignore 8-bit (iso14443 starts with LSBit = bit 1)
        # fixes wrong type for manufacturer Infineon
        # (http://nfc-tools.org/index.php?title=ISO14443A)
        if self.sak != None:
            tmp_sak = self.sak & 0x7F
            try:
                picc_type = PICC_Type(tmp_sak)
            except ValueError:
                logger_debug.error(
                    _F('Unkown SAK value [{}], cannot identify PICC type, returning UNKNOWN', format_hex([tmp_sak])))

        return picc_type

    def __str__(self):
        return '<UID: [{}], SAK: {:#04x}, Type: {}>'.format(format_hex(self.uid()), self.sak if self.sak else 0, self.get_picc_type())


class MIFARE_Key(object):
    '''
    A struct used for passing a MIFARE Crypto1 key
    '''
    # A Mifare Crypto1 key is 6 bytes. All keys are set to FFFFFFFFFFFFh at
    # chip delivery from the factory.
    key_byte = [0xFF] * 6

    def __str__(self):
        return '<MIFARE_Key: [{}]>'.format(format_hex(self.key_byte))


#=========================================================================
# MFRC522
#=========================================================================

class MFRC522(object):
    '''
    TODO
    '''

    # Firmware data for self-test
    # Reference values based on firmware version
    # Hint: if needed, you can remove unused self-test data to save flash memory
    #
    # Version 0.0 (0x90)
    # Philips Semiconductors; Preliminary Specification Revision 2.0 - 01
    # August 2005; 16.1 self-test
    MFRC522_firmware_referenceV0_0 = [
        0x00, 0x87, 0x98, 0x0f, 0x49, 0xFF, 0x07, 0x19,
        0xBF, 0x22, 0x30, 0x49, 0x59, 0x63, 0xAD, 0xCA,
        0x7F, 0xE3, 0x4E, 0x03, 0x5C, 0x4E, 0x49, 0x50,
        0x47, 0x9A, 0x37, 0x61, 0xE7, 0xE2, 0xC6, 0x2E,
        0x75, 0x5A, 0xED, 0x04, 0x3D, 0x02, 0x4B, 0x78,
        0x32, 0xFF, 0x58, 0x3B, 0x7C, 0xE9, 0x00, 0x94,
        0xB4, 0x4A, 0x59, 0x5B, 0xFD, 0xC9, 0x29, 0xDF,
        0x35, 0x96, 0x98, 0x9E, 0x4F, 0x30, 0x32, 0x8D]
    # Version 1.0 (0x91)
    # NXP Semiconductors; Rev. 3.8 - 17 September 2014; 16.1.1 self-test
    MFRC522_firmware_referenceV1_0 = [
        0x00, 0xC6, 0x37, 0xD5, 0x32, 0xB7, 0x57, 0x5C,
        0xC2, 0xD8, 0x7C, 0x4D, 0xD9, 0x70, 0xC7, 0x73,
        0x10, 0xE6, 0xD2, 0xAA, 0x5E, 0xA1, 0x3E, 0x5A,
        0x14, 0xAF, 0x30, 0x61, 0xC9, 0x70, 0xDB, 0x2E,
        0x64, 0x22, 0x72, 0xB5, 0xBD, 0x65, 0xF4, 0xEC,
        0x22, 0xBC, 0xD3, 0x72, 0x35, 0xCD, 0xAA, 0x41,
        0x1F, 0xA7, 0xF3, 0x53, 0x14, 0xDE, 0x7E, 0x02,
        0xD9, 0x0F, 0xB5, 0x5E, 0x25, 0x1D, 0x29, 0x79]
    # Version 2.0 (0x92)
    # NXP Semiconductors; Rev. 3.8 - 17 September 2014; 16.1.1 self-test
    MFRC522_firmware_referenceV2_0 = [
        0x00, 0xEB, 0x66, 0xBA, 0x57, 0xBF, 0x23, 0x95,
        0xD0, 0xE3, 0x0D, 0x3D, 0x27, 0x89, 0x5C, 0xDE,
        0x9D, 0x3B, 0xA7, 0x00, 0x21, 0x5B, 0x89, 0x82,
        0x51, 0x3A, 0xEB, 0x02, 0x0C, 0xA5, 0x00, 0x49,
        0x7C, 0x84, 0x4D, 0xB3, 0xCC, 0xD2, 0x1B, 0x81,
        0x5D, 0x48, 0x76, 0xD5, 0x71, 0x61, 0x21, 0xA9,
        0x86, 0x96, 0x83, 0x38, 0xCF, 0x9D, 0x5B, 0x6D,
        0xDC, 0x15, 0xBA, 0x3E, 0x7D, 0x95, 0x3B, 0x2F]
    # Clone
    # Fudan Semiconductor FM17522 (0x88)
    FM17522_firmware_reference = [
        0x00, 0xD6, 0x78, 0x8C, 0xE2, 0xAA, 0x0C, 0x18,
        0x2A, 0xB8, 0x7A, 0x7F, 0xD3, 0x6A, 0xCF, 0x0B,
        0xB1, 0x37, 0x63, 0x4B, 0x69, 0xAE, 0x91, 0xC7,
        0xC3, 0x97, 0xAE, 0x77, 0xF4, 0x37, 0xD7, 0x9B,
        0x7C, 0xF5, 0x3C, 0x11, 0x8F, 0x15, 0xC3, 0xD7,
        0xC1, 0x5B, 0x00, 0x2A, 0xD0, 0x75, 0xDE, 0x9E,
        0x51, 0x64, 0xAB, 0x3E, 0xE9, 0x15, 0xB5, 0xAB,
        0x56, 0x9A, 0x98, 0x82, 0x26, 0xEA, 0x2A, 0x62]

    def __init__(self, bus=0, device=0, speed=1000000, pin_reset=25, pin_ce=0, pin_irq=24, pin_mode=GPIO.BCM):
        '''
        Create a new MFRC522 instance

        @param bus: The SPI bus (default = 0)
        @param device: The SPI device (default = 0)
        @param speed: The max speed in Hz for the SPI device (default = 1000000)
        @param pin_reset: The GPIO reset pin number (default = 25)
        @param pin_ce: The GPIO chip select pin number (default = 0, not connected)
        @param pin_irq: The GPIO IRQ pin number (default = 24)
        @param pin_mode: GPIO pin numbering mode (default = GPIO.BCM)
        '''
        self.__log_trace = logger_trace.isEnabledFor(logging.DEBUG)
        self.__log_spi = logger_spi.isEnabledFor(logging.DEBUG)
        self.__log_debug = logger_debug.isEnabledFor(logging.DEBUG)

        self.bus = bus
        self.device = device
        self.speed = speed
        self.pin_reset = pin_reset
        self.pin_ce = pin_ce
        self.pin_irq = pin_irq
        self.pin_mode = pin_mode

        self.spi = spidev.SpiDev()

    #=========================================================================
    # Basic interface functions for communicating with the MFRC522
    #=========================================================================

    def _spi_transfer(self, data):
        '''
        Transfer data from and to the pcd

        @param data: List of bytes to write to the pcd
        @return: List of bytes read from the pcd
        '''
        if self.pin_ce != 0:
            GPIO.output(self.pin_ce, 0)     # release chip-select
        # MSB == 0 is for writing. LSB is not used in address. Datasheet
        # section 8.1.2.3.
        rx = self.spi.xfer2(data)
        if self.pin_ce != 0:
            GPIO.output(self.pin_ce, 1)     # reactivated chip-select

        if self.__log_spi:
            logger_spi.debug(
                _F(' receive [{}]', ' '.join(format(x, '#04x') for x in rx)))
        return rx

    def pcd_write_register(self, reg, val):
        '''
        Writes a byte to the specified register in the MFRC522 chip.
        The interface is described in the datasheet section 8.1.2.

        @param reg: The register to write to. One of the PCD_Register enums
        @param val: The value to write
        '''
        if self.__log_spi:
            logger_spi.debug(
                _F('write_register \'{reg_name}\': [{reg_val:#04x} {val:#04x}]', reg_name=reg.name, reg_val=reg.value, val=val))

        self._spi_transfer([reg.value, val])

    def pcd_write_register2(self, reg, vals):
        '''
        Writes a list of bytes to the specified register in the MFRC522 chip.
        The interface is described in the datasheet section 8.1.2.

        @param reg: The register to write to. One of the PCD_Register enums
        @param vals: The list of values to write
        '''
        if self.__log_spi:
            logger_spi.debug(
                _F('write_register2 \'{reg_name}\': [{reg_val:#04x} {values}]', reg_name=reg.name, reg_val=reg.value, values=format_hex(vals)))

        self._spi_transfer([reg.value] + vals)

    def pcd_read_register(self, reg):
        '''
        Reads a byte from the specified register in the MFRC522 chip.
        The interface is described in the datasheet section 8.1.2.

        @param reg: The register to read from. One of the PCD_Register enums
        @return: The byte value read from the register
        '''
        # MSB == 1 is for reading. LSB is not used in address. Datasheet section 8.1.2.3.
        # Send 0 to stop reading.
        result = self._spi_transfer([reg.value | 0x80, 0])[1]

        if self.__log_spi:
            logger_spi.debug(
                _F('read_register \'{reg_name}\': {reg_val:#04x} result: [{result:#04x}]', reg_name=reg.name, reg_val=reg.value, result=result))

        return result

    def pcd_read_register2(self, reg, count, rx_align):
        '''
        Reads a number of bytes from the specified register in the MFRC522 chip.
        The interface is described in the datasheet section 8.1.2.

        @param reg: The register to read from. One of the PCD_Register enums
        @param count: The number of bytes to read
        @param rx_align: Only bit positions rxAlign..7 in values[0] are updated.
        @return: The byte value read from the register
        '''
        if count <= 0:
            if self.__log_debug:
                logger_debug.warn('read_register called with count <= 0')
            return []

        # MSB == 1 is for reading. LSB is not used in address. Datasheet
        # section 8.1.2.3.
        address = 0x80 | reg.value
        index = 0                               # Index in values array.
        _count = count
        tx = []

        _count -= 1                             # One read is performed outside of the loop
        # Tell MFRC522 which address we want to read
        tx.append(address)

        # Only update bit positions rxAlign..7 in values[0]
        if rx_align:
            # Read value and tell that we want to read the same address again.
            tx.append(address)
            index += 1

        for __ in range(index, _count):
            tx.append(address)

        # Read the final byte. Send 0 to stop reading.
        tx.append(0)

        rx = self._spi_transfer(tx)
        # Remove the first read byte (from initializing reading the register)
        rx.pop(0)

        # Only update bit positions rxAlign..7 in values[0]
        if rx_align:
            # Create bit mask for bit positions rxAlign..7
            mask = (0xFF << rx_align) & 0xFF
            # Apply mask to both current value of values[0] and the new data in
            # value.
            # values[0] = (values[0] & ~mask) | (value & mask);
            rx[0] = (rx[0] & ~mask) | (rx[0] & mask)

        if self.__log_spi:
            logger_spi.debug(
                _F('read_register2 \'{reg_name}\': {reg_val:#04x}, count: {count}, rx_align: {rx_align}, result: [{values}]', reg_name=reg.name, reg_val=reg.value, count=count, rx_align=rx_align, values=format_hex(rx)))

        return rx

    def pcd_set_register_bitmask(self, reg, mask):
        '''
        Sets the bits given in mask in register reg..

        @param reg: The register to update. One of the PCD_Register enums
        @param mask: he bits to set
        '''
        tmp = self.pcd_read_register(reg)
        self.pcd_write_register(reg, tmp | mask)

    def pcd_clear_register_bitmask(self, reg, mask):
        '''
        Clears the bits given in mask from register reg.

        @param reg: The register to update. One of the PCD_Register enums
        @param mask: The bits to clear
        '''
        tmp = self.pcd_read_register(reg)
        self.pcd_write_register(reg, tmp & (~mask))

    def pcd_calulate_crc(self, data):
        '''
        Use the CRC coprocessor in the MFRC522 to calculate a CRC_A.

        Returns STATUS_OK on success, STATUS_TIMEOUT if the CRC calculation did not complete in time (communication with the MFRC522 might be down)

        @param data: The data to transfer to the FIFO for CRC calculation (list of bytes to transfer).
        @return: (StatusCode, result) - result is exactly 2 bytes long
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_calculate_crc')

        # Stop any active command.
        self.pcd_write_register(PCD_Register.CommandReg,
                                PCD_Command.PCD_Idle.value)
        # Clear the CRCIRq interrupt request bit
        self.pcd_write_register(PCD_Register.DivIrqReg, 0x04)
        # FlushBuffer = 1, FIFO initialization
        self.pcd_write_register(PCD_Register.FIFOLevelReg, 0x80)
        # Write data to the FIFO
        self.pcd_write_register2(PCD_Register.FIFODataReg, data)
        # Start the calculation
        self.pcd_write_register(PCD_Register.CommandReg,
                                PCD_Command.PCD_CalcCRC.value)

        # Wait for the CRC calculation to complete.
        #    // Arduino Uno 16bit
        #    // Wait for the CRC calculation to complete. Each iteration of the while-loop takes 17.73us.
        #    for (uint16_t i = 5000; i > 0; i--) { ... }
        for __ in range(255):
            # DivIrqReg[7..0] bits are: Set2 reserved reserved MfinActIRq
            # reserved CRCIRq reserved reserved
            n = self.pcd_read_register(PCD_Register.DivIrqReg)
            # CRCIRq bit set - calculation done
            if n & 0x04:
                # Stop calculating CRC for new content in the FIFO.
                self.pcd_write_register(
                    PCD_Register.CommandReg, PCD_Command.PCD_Idle.value)
                result = []
                result.append(self.pcd_read_register(
                    PCD_Register.CRCResultRegL))
                result.append(self.pcd_read_register(
                    PCD_Register.CRCResultRegH))
                return StatusCode.STATUS_OK, result

        # Timeout: Communication with the MFRC522 might be down.
        if self.__log_debug:
            logger_debug.warn(
                'Timeout during CRC_A calculation. Communication with the MFRC522 might be down')
        return StatusCode.STATUS_TIMEOUT, None

    #=========================================================================
    # Functions for manipulating the MFRC522
    #=========================================================================

    def pcd_init(self):
        '''
        Initializes the MFRC522 chip
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_init')

        # Setup SPI
        if self.__log_debug:
            logger_debug.info(
                _F('Init spidev with bus={bus}, device={device}, speed={speed}', bus=self.bus, device=self.device, speed=self.speed))

        self.spi.open(self.bus, self.device)
        self.spi.max_speed_hz = self.speed

        # Setup GPIO
        if self.__log_debug:
            logger_debug.info(_F('Init GPIO with mode={mode}, pin_reset={pin_reset}, pin_ce={pin_ce}, pin_irq={pin_irq}',
                                 mode=self.pin_mode, pin_reset=self.pin_reset, pin_ce=self.pin_ce, pin_irq=self.pin_irq))
        GPIO.setmode(self.pin_mode)
        if self.pin_irq != 0:
            GPIO.setup(self.pin_irq, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #GPIO.add_event_detect(self.pin_irq, GPIO.FALLING, callback=self.IRQ_Callback)
        if self.pin_ce != 0:
            GPIO.setup(self.pin_ce, GPIO.OUT)
            GPIO.output(self.pin_ce, 1)

        # If a valid pin number has been set, pull device out of power down /
        # reset state.
        hard_reset = False
        if self.pin_reset != 0:
            # First set the resetPowerDownPin as digital input, to check the
            # MFRC522 power down mode.
            GPIO.setup(self.pin_reset, GPIO.IN)
            # The MFRC522 chip is in power down mode.
            if GPIO.input(self.pin_reset) == GPIO.LOW:
                if self.__log_debug:
                    logger_debug.debug(
                        'MFRC522 is in power down mode. Trigger a hard reset')
                # Now set the resetPowerDownPin as digital output.
                GPIO.setup(self.pin_reset, GPIO.OUT)
                # Make shure we have a clean LOW state.
                GPIO.output(self.pin_reset, 0)
                # 8.8.1 Reset timing requirements says about 100ns. Let us be
                # generous: 2μsl
                usleep(2)
                # Exit power down mode. This triggers a hard reset.
                GPIO.output(self.pin_reset, 1)
                # Section 8.8.2 in the datasheet says the oscillator start-up
                # time is the start up time of the crystal + 37,74μs. Let us be
                # generous: 50ms.
                sleep(0.05)
                hard_reset = True

        if not hard_reset:      # Perform a soft reset if we haven't triggered a hard reset above.
            if self.__log_debug:
                logger_debug.debug(
                    'MFRC522 is not in power down mode. Perform a soft reset')
            self.pcd_reset()

        # Reset baud rates
        self.pcd_write_register(PCD_Register.TxModeReg, 0x00)
        self.pcd_write_register(PCD_Register.RxModeReg, 0x00)
        # Reset ModWidthReg
        self.pcd_write_register(PCD_Register.ModWidthReg, 0x26)

        # When communicating with a PICC we need a timeout if something goes wrong.
        # f_timer = 13.56 MHz / (2*TPreScaler+1) where TPreScaler = [TPrescaler_Hi:TPrescaler_Lo].
        # TPrescaler_Hi are the four low bits in TModeReg. TPrescaler_Lo is
        # TPrescalerReg.
        # TAuto=1; timer starts automatically at the end of the transmission in
        # all communication modes at all speeds
        self.pcd_write_register(PCD_Register.TModeReg, 0x80)
        # TPreScaler = TModeReg[3..0]:TPrescalerReg, ie 0x0A9 = 169 =>
        # f_timer=40kHz, ie a timer period of 25 micro seconds.
        self.pcd_write_register(PCD_Register.TPrescalerReg, 0xA9)
        # Reload timer with 0x3E8 = 1000, ie 25ms before timeout.
        self.pcd_write_register(PCD_Register.TReloadRegH, 0x03)
        self.pcd_write_register(PCD_Register.TReloadRegL, 0xE8)

        # Default 0x00. Force a 100 % ASK modulation independent of the
        # ModGsPReg register setting
        self.pcd_write_register(PCD_Register.TxASKReg, 0x40)
        # Default 0x3F. Set the preset value for the CRC coprocessor for the
        # CalcCRC command to 0x6363 (ISO 14443-3 part 6.2.4)
        self.pcd_write_register(PCD_Register.ModeReg, 0x3D)
        # Enable the antenna driver pins TX1 and TX2 (they were disabled by the
        # reset)
        self.antenna_on()

    def pcd_cleanup(self):
        '''
        Cleanup GPIO and close SPI device
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_cleanup')

        pins = []
        if self.pin_ce > 0:
            pins.append(self.pin_ce)
        if self.pin_irq > 0:
            pins.append(self.pin_irq)
        if self.pin_reset > 0:
            pins.append(self.pin_reset)

        if len(pins) > 0:
            GPIO.cleanup(pins)
        self.spi.close()

    def pcd_reset(self):
        '''
        Performs a soft reset on the MFRC522 chip and waits for it to be ready again.
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_reset')

        # Issue the SoftReset command.
        self.pcd_write_register(PCD_Register.CommandReg,
                                PCD_Command.PCD_SoftReset.value)
        # The datasheet does not mention how long the SoftRest command takes to complete.
        # But the MFRC522 might have been in soft power-down mode (triggered by bit 4 of CommandReg)
        # Section 8.8.2 in the datasheet says the oscillator start-up time is
        # the start up time of the crystal + 37,74 micro seconds. Let us be
        # generous: 50ms.
        for __ in range(3):
            # Wait for the PowerDown bit in CommandReg to be cleared (max
            # 3x50ms)
            sleep(0.05)
            if not (self.pcd_read_register(PCD_Register.CommandReg) & (1 << 4)):
                break

    def antenna_on(self):
        '''
        Turns the antenna on by enabling pins TX1 and TX2.
        After a reset these pins are disabled.
        '''
        if self.__log_trace:
            logger_trace.debug('>> antenna_on')

        temp = self.pcd_read_register(PCD_Register.TxControlReg)
        if (~(temp & 0x03)):
            self.pcd_write_register(PCD_Register.TxControlReg, temp | 0x03)

    def antenna_off(self):
        '''
        Turns the antenna off by disabling pins TX1 and TX2.
        '''
        if self.__log_trace:
            logger_trace.debug('>> antenna_off')

        self.pcd_clear_register_bitmask(PCD_Register.TxControlReg, 0x03)

    def pcd_get_antenna_gain(self):
        '''
        Get the current MFRC522 Receiver Gain (RxGain[2:0]) value.
        See 9.3.3.6 / table 98 in http://www.nxp.com/documents/data_sheet/MFRC522.pdf
        NOTE: Return value scrubbed with (0x07<<4)=01110000b as RCFfgReg may use reserved bits.

        @return: Value of the RxGain, scrubbed to the 3 bits used.
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_get_antenna_gain')

        return self.pcd_read_register(PCD_Register.RFCfgReg) & (0x07 << 4)

    def pcd_set_antenna_gain(self, mask):
        '''
        Set the MFRC522 Receiver Gain (RxGain) to value specified by given mask.
        See 9.3.3.6 / table 98 in http://www.nxp.com/documents/data_sheet/MFRC522.pdf
        NOTE: Given mask is scrubbed with (0x07<<4)=01110000b as RCFfgReg may use reserved bits.
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_set_antenna_gain')

        # only bother if there is a change
        if self.pcd_get_antenna_gain() != mask:
            # clear needed to allow 000 pattern
            self.pcd_clear_register_bitmask(PCD_Register.RFCfgReg, (0x07 << 4))
            self.pcd_set_register_bitmask(PCD_Register.RFCfgReg, mask & (
                0x07 << 4))   # only set RxGain[2:0] bits

    def pcd_perform_self_test(self):
        '''
        Performs a self-test of the MFRC522
        See 16.1.1 in http://www.nxp.com/documents/data_sheet/MFRC522.pdf

        @return: Whether or not the test passed. Or false if no firmware reference is available.
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_perform_self_test')

        # This follows directly the steps outlined in 16.1.1
        # 1. Perform a soft reset.
        self.pcd_reset()

        # 2. Clear the internal buffer by writing 25 bytes of 00h
        zeroes = [0] * 25
        # flush the FIFO buffer
        self.pcd_write_register(PCD_Register.FIFOLevelReg, 0x80)
        # write 25 bytes of 00h to FIFO
        self.pcd_write_register2(PCD_Register.FIFODataReg, zeroes)
        # transfer to internal buffer
        self.pcd_write_register(PCD_Register.CommandReg,
                                PCD_Command.PCD_Mem.value)

        # 3. Enable self-test
        self.pcd_write_register(PCD_Register.AutoTestReg, 0x09)

        # 4. Write 00h to FIFO buffer
        self.pcd_write_register(PCD_Register.FIFODataReg, 0x00)

        # 5. Start self-test by issuing the CalcCRC command
        self.pcd_write_register(PCD_Register.CommandReg,
                                PCD_Command.PCD_CalcCRC.value)

        # 6. Wait for self-test to complete
        for __ in range(255):
            # The datasheet does not specify exact completion condition except
            # that FIFO buffer should contain 64 bytes.
            # While selftest is initiated by CalcCRC command
            # it behaves differently from normal CRC computation,
            # so one can't reliably use DivIrqReg to check for completion.
            # It is reported that some devices does not trigger CRCIRq flag
            # during selftest.
            n = self.pcd_read_register(PCD_Register.FIFOLevelReg)
            if n >= 64:
                break

        # Stop calculating CRC for new content in the FIFO.
        self.pcd_write_register(PCD_Register.CommandReg,
                                PCD_Command.PCD_Idle.value)

        # 7. Read out resulting 64 bytes from the FIFO buffer.
        result = self.pcd_read_register2(PCD_Register.FIFODataReg, 64, 0)

        # Auto self-test done
        # Reset AutoTestReg register to be 0 again. Required for normal
        # operation.
        self.pcd_write_register(PCD_Register.AutoTestReg, 0x00)

        # Determine firmware version (see section 9.3.4.8 in spec)
        version = self.pcd_read_register(PCD_Register.VersionReg)

        # Pick the appropriate reference values
        # const byte *reference;
        if version == 0x88:    # Fudan Semiconductor FM17522 clone
            reference = self.FM17522_firmware_reference
        elif version == 0x90:    # Version 0.0
            reference = self.MFRC522_firmware_referenceV0_0
        elif version == 0x91:    # Version 1.0
            reference = self.MFRC522_firmware_referenceV1_0
        elif version == 0x92:    # Version 2.0
            reference = self.MFRC522_firmware_referenceV2_0
        else:  # Unknown version
            return False  # abort test

        # Verify that the results match up to our expectations
        for i in range(64):
            if result[i] != reference[i]:
                return False

        # Test passed; all is good.
        return True

    #=========================================================================
    # Power control
    #=========================================================================

    # IMPORTANT NOTE!!!!
    # Calling any other function that uses CommandReg will disable soft power down mode !!!
    # For more details about power control, refer to the datasheet - page 33
    # (8.6)

    def pcd_soft_power_down(self):
        '''
        Note : Only soft power down mode is available throught software
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_soft_power_down')
        # Read state of the command register
        val = self.pcd_read_register(PCD_Register.CommandReg)
        # set PowerDown bit ( bit 4 ) to 1
        val |= (1 << 4)
        # write new value to the command register
        self.pcd_write_register(PCD_Register.CommandReg, val)

    def pcd_soft_power_up(self):
        '''
        MFRC522::PCD_SoftPowerUp
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_soft_power_up')
        # Read state of the command register
        val = self.pcd_read_register(PCD_Register.CommandReg)
        # set PowerDown bit ( bit 4 ) to 0
        val &= ~(1 << 4)
        # write new value to the command register
        self.pcd_write_register(PCD_Register.CommandReg, val)

        # wait until PowerDown bit is cleared (this indicates end of wake up
        # procedure)
        for __ in range(125):       # On Arduino timeout is set to 500 ms
            # Read state of the command register
            val = self.pcd_read_register(PCD_Register.CommandReg)
            # if powerdown bit is 0
            if not (val & (1 << 4)):
                # wake up procedure is finished
                break

    #=========================================================================
    # Functions for communicating with PICCs
    #=========================================================================

    def pcd_transceive_data(self, send_data, wants_back_data=False, tx_valid_bits=0, rx_align=0, check_crc=False):
        '''
        Executes the Transceive command.
        CRC validation can only be done if backData and backLen are specified.

        @param send_data: The data to transfer to the FIFO (list of bytes).
        @param wants_back_data: True if data should be read back after executing the command.
        @param tx_valid_bits: The number of valid bits in the last byte. 0 for 8 valid bits.
        @param rx_align: Defines the bit position in back_data[0] for the first bit received. Default 0.
        @param check_crc: True => The last two bytes of the response is assumed to be a CRC_A that must be validated.
        @return: (StatusCode, rx_back_data, rx_valid_bits)
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_transceive_data')

        wait_irq = 0x30     # RxIRq and IdleIRq
        return self.pcd_communicate_with_picc(PCD_Command.PCD_Transceive, wait_irq, send_data, wants_back_data, tx_valid_bits, rx_align, check_crc)

    def pcd_communicate_with_picc(self, command, wait_irq, send_data, wants_back_data, tx_valid_bits, rx_align=0, check_crc=False):
        '''
        Transfers data to the MFRC522 FIFO, executes a command, waits for completion and transfers data back from the FIFO.
        CRC validation can only be done if backData and backLen are specified.

        @param command: The command to execute. One of the PCD_Command enums.
        @param wait_irq: The bits in the ComIrqReg register that signals successful completion of the command.
        @param send_data: The data to transfer to the FIFO (list of bytes).
        @param wants_back_data: True if data should be read back after executing the command.
        @param tx_valid_bits: The number of valid bits in the last byte. 0 for 8 valid bits.
        @param rx_align: Defines the bit position in back_data[0] for the first bit received. Default 0.
        @param check_crc: True => The last two bytes of the response is assumed to be a CRC_A that must be validated.
        @return: (StatusCode, rx_back_data, rx_valid_bits)
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_communicate_with_pic')

        # Prepare values for BitFramingReg
        # RxAlign = BitFramingReg[6..4]. TxLastBits = BitFramingReg[2..0]
        bit_framing = (rx_align << 4) + tx_valid_bits

        # Stop any active command.
        self.pcd_write_register(PCD_Register.CommandReg,
                                PCD_Command.PCD_Idle.value)
        # Clear all seven interrupt request bits
        self.pcd_write_register(PCD_Register.ComIrqReg, 0x7F)
        # FlushBuffer = 1, FIFO initialization
        self.pcd_write_register(PCD_Register.FIFOLevelReg, 0x80)
        # Write sendData to the FIFO
        self.pcd_write_register2(PCD_Register.FIFODataReg, send_data)
        # Bit adjustments
        self.pcd_write_register(PCD_Register.BitFramingReg, bit_framing)
        # Execute the command
        self.pcd_write_register(PCD_Register.CommandReg, command.value)

        if command == PCD_Command.PCD_Transceive:
            # StartSend=1, transmission of data starts
            self.pcd_set_register_bitmask(PCD_Register.BitFramingReg, 0x80)

        # Wait for the command to complete.
        # In PCD_Init() we set the TAuto flag in TModeReg. This means the timer automatically starts when the PCD stops transmitting.
        #    // Arduino Uno 16bit
        #    // Wait for the command to complete. Each iteration of the while-loop takes 17.73us.
        #    for (i = 2000; i > 0; i--) { ... }
        for i in range(125, 0, -1):
            # ComIrqReg[7..0] bits are: Set1 TxIRq RxIRq IdleIRq HiAlertIRq
            # LoAlertIRq ErrIRq TimerIRq
            n = self.pcd_read_register(PCD_Register.ComIrqReg)
            # One of the interrupts that signal success has been set.
            if n & wait_irq:
                break
            if n & 0x01:                                                # Timer interrupt - nothing received in 25ms
                return StatusCode.STATUS_TIMEOUT, None, None

        # Timout (on Ardunion 35.7ms) and nothing happend. Communication with
        # the MFRC522 might be down.
        if i == 0:
            if self.__log_debug:
                logger_debug.warn(
                    _F('Timeout during communication with PICC (Command={}). Communication with the MFRC522 might be down', command.name))
            return StatusCode.STATUS_TIMEOUT, None, None

        # Stop now if any errors except collisions were detected.
        # ErrorReg[7..0] bits are: WrErr TempErr reserved BufferOvfl CollErr
        # CRCErr ParityErr ProtocolErr
        error_reg_value = self.pcd_read_register(PCD_Register.ErrorReg)
        if error_reg_value & 0x13:                                              # BufferOvfl ParityErr ProtocolErr
            if self.__log_debug:
                logger_debug.warn(
                    _F('Error detected during communication with PICC (Command={}). Error register value: {:#04x}', command.name, error_reg_value))
            return StatusCode.STATUS_ERROR, None, None

        rx_valid_bits = 0

        # If the caller wants data back, get it from the MFRC522.
        rx_back_data = []
        rx_back_data_len = 0
        if wants_back_data:
            if self.__log_trace:
                logger_trace.debug(
                    '>> pcd_communicate_with_pic: read back data')
            # Number of bytes in the FIFO
            n = self.pcd_read_register(PCD_Register.FIFOLevelReg)
            if n > 0:
                rx_back_data = self.pcd_read_register2(
                    PCD_Register.FIFODataReg, n, rx_align)    # Get received data from FIFO
                rx_back_data_len = len(rx_back_data)
            # RxLastBits[2:0] indicates the number of valid bits in the last
            # received byte. If this value is 000b, the whole byte is valid.
            rx_valid_bits = self.pcd_read_register(
                PCD_Register.ControlReg) & 0x07

        # Tell about collisions
        if error_reg_value & 0x08:        # CollErr
            if self.__log_debug:
                logger_debug.debug(
                    _F('Collision detected during communication with PICC (Command={}). Error register value: {:#04x}', command.name, error_reg_value))
            return StatusCode.STATUS_COLLISION, rx_back_data, rx_valid_bits

        # Perform CRC_A validation if requested.
        if wants_back_data and rx_back_data_len > 0 and check_crc:
            if self.__log_trace:
                logger_trace.debug(
                    '>> pcd_communicate_with_pic: CRC_A validation for back data')
            # In this case a MIFARE Classic NAK is not OK.
            if rx_back_data_len == 1 and rx_valid_bits == 4:
                if self.__log_debug:
                    logger_debug.warn(
                        _F('Communication with PICC resulted in MIFARE Classic NAK (Command={})', command.name))
                return StatusCode.STATUS_MIFARE_NACK, rx_back_data, rx_valid_bits
            # We need at least the CRC_A value and all 8 bits of the last byte
            # must be received.
            if rx_back_data_len < 2 or rx_valid_bits != 0:
                if self.__log_debug:
                    logger_debug.warn(
                        _F('Not enough bits for CRC_A calculation received from communication with PICC (Command={})', command.name))
                return StatusCode.STATUS_CRC_WRONG, rx_back_data, rx_valid_bits
            # Verify CRC_A - do our own calculation and store the control in
            # controlBuffer.
            status, control_buffer = self.pcd_calulate_crc(
                rx_back_data[:rx_back_data_len - 2])
            if status != StatusCode.STATUS_OK:
                return status, rx_back_data, rx_valid_bits
            if (rx_back_data[rx_back_data_len - 2] != control_buffer[0]) or (rx_back_data[rx_back_data_len - 1] != control_buffer[1]):
                if self.__log_debug:
                    logger_debug.warn(_F('Wrong CRC_A value received from communication with PICC (Command: {}, expected: [ {:#04x} {:#04x} ], actual: [ {:#04x} {:#04x} ])',
                                         command.name, rx_back_data[rx_back_data_len - 2], rx_back_data[rx_back_data_len - 1], control_buffer[0], control_buffer[1]))
                return StatusCode.STATUS_CRC_WRONG, None, None

        return StatusCode.STATUS_OK, rx_back_data, rx_valid_bits

    def picc_request_a(self):
        '''
        Transmits a REQuest command, Type A. Invites PICCs in state IDLE to go to READY and prepare for anticollision or selection. 7 bit frame.
        Beware: When two PICCs are in the field at the same time I often get STATUS_TIMEOUT - probably due do bad antenna design.

        @return: (StatusCode, rx_back_data) - rx_back_data contains the ATQA (Answer to request, exactly 16 bits)
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_request_a')

        return self.picc_reqa_or_wupa(PICC_Command.PICC_CMD_REQA)

    def picc_wakeup_a(self):
        '''
        Transmits a Wake-UP command, Type A. Invites PICCs in state IDLE and HALT to go to READY(*) and prepare for anticollision or selection. 7 bit frame.
        Beware: When two PICCs are in the field at the same time I often get STATUS_TIMEOUT - probably due do bad antenna design.

        @return: (StatusCode, rx_back_data) - rx_back_data contains the ATQA (Answer to request, exactly 16 bits)
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_wakeup_a')

        return self.picc_reqa_or_wupa(PICC_Command.PICC_CMD_WUPA)

    def picc_reqa_or_wupa(self, command):
        '''
        Transmits REQA or WUPA commands.
        Beware: When two PICCs are in the field at the same time I often get STATUS_TIMEOUT - probably due do bad antenna design.

        @param command: The command to send - PICC_CMD_REQA or PICC_CMD_WUPA
        @return: (StatusCode, rx_back_data) - rx_back_data contains the ATQA (Answer to request, exactly 16 bits)
        '''
        self.pcd_clear_register_bitmask(
            PCD_Register.CollReg, 0x80)  # ValuesAfterColl=1 => Bits received after collision are cleared.
        # For REQA and WUPA we need the short frame format - transmit only 7
        # bits of the last (and only) byte. TxLastBits = BitFramingReg[2..0]
        tx_valid_bits = 7
        status, rx_back_data, rx_valid_bits = self.pcd_transceive_data(
            [command.value], True, tx_valid_bits)
        if status != StatusCode.STATUS_OK:
            return status, rx_back_data
        # ATQA must be exactly 16 bits.
        if len(rx_back_data) != 2 or rx_valid_bits != 0:
            return StatusCode.STATUS_ERROR, rx_back_data
        return StatusCode.STATUS_OK, rx_back_data

    def picc_select(self, uid=None, rx_valid_bits=0):
        '''
        Transmits SELECT/ANTICOLLISION commands to select a single PICC.
        Before calling this function the PICCs must be placed in the READY(*) state by calling PICC_RequestA() or PICC_WakeupA().
        On success:
                - The chosen PICC is in state ACTIVE(*) and all other PICCs have returned to state IDLE/HALT. (Figure 7 of the ISO/IEC 14443-3 draft.)
                - The UID size and value of the chosen PICC is returned in *uid along with the SAK.

        A PICC UID consists of 4, 7 or 10 bytes.
        Only 4 bytes can be specified in a SELECT command, so for the longer UIDs two or three iterations are used:
                UID size    Number of UID bytes        Cascade levels        Example of PICC
                ========    ===================        ==============        ===============
                single                 4                        1                MIFARE Classic
                double                 7                        2                MIFARE Ultralight
                triple                10                        3                Not currently in use?

        @param uid: Optional, can be used to supply a known UID.
        @param rx_valid_bits: The number of known UID bits supplied in *uid. Normally 0. If set you must also supply uid->size.
        @return (StatusCode, Uid)
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_select')

        _uid = uid if uid else Uid()
        # bool selectDone;
        # useCascadeTag;
        cascade_level = 1
        # MFRC522::StatusCode result;
        # byte count;
        # byte checkBit;
        # byte index;
        # The first index in uid->uidByte[] that is used in the current Cascade
        # Level.
        uid_index = 0
        # int8_t currentLevelKnownBits;        // The number of known UID bits in the current Cascade Level.
        # byte _buffer[9];                    // The SELECT/ANTICOLLISION
        # commands uses a 7 byte standard frame + 2 bytes CRC_A
        # The SELECT/ANTICOLLISION commands uses a 7 byte standard frame + 2
        # bytes CRC_A
        _buffer = [0] * 9
        # The number of bytes used in the _buffer, ie the number of bytes to
        # transfer to the FIFO.
        buffer_used = 0
        # byte rxAlign;                    // Used in BitFramingReg. Defines the bit position for the first bit received.
        # byte txLastBits;                // Used in BitFramingReg. The number of valid bits in the last transmitted byte.
        # byte *responseBuffer;
        # byte responseLength;

        # Description of _buffer structure:
        #        Byte 0: SEL                 Indicates the Cascade Level: PICC_CMD_SEL_CL1, PICC_CMD_SEL_CL2 or PICC_CMD_SEL_CL3
        #        Byte 1: NVB                    Number of Valid Bits (in complete command, not just the UID): High nibble: complete bytes, Low nibble: Extra bits.
        #        Byte 2: UID-data or CT        See explanation below. CT means Cascade Tag.
        #        Byte 3: UID-data
        #        Byte 4: UID-data
        #        Byte 5: UID-data
        #        Byte 6: BCC                    Block Check Character - XOR of bytes 2-5
        #        Byte 7: CRC_A
        #        Byte 8: CRC_A
        # The BCC and CRC_A are only transmitted if we know all the UID bits of the current Cascade Level.
        #
        # Description of bytes 2-5: (Section 6.5.4 of the ISO/IEC 14443-3 draft: UID contents and cascade levels)
        #        UID size    Cascade level    Byte2    Byte3    Byte4    Byte5
        #        ========    =============    =====    =====    =====    =====
        #         4 bytes        1            uid0    uid1    uid2    uid3
        #         7 bytes        1            CT        uid0    uid1    uid2
        #                        2            uid3    uid4    uid5    uid6
        #        10 bytes        1            CT        uid0    uid1    uid2
        #                        2            CT        uid3    uid4    uid5
        #                        3            uid6    uid7    uid8    uid9

        # Sanity checks
        if rx_valid_bits > 80:
            if self.__log_debug:
                logger_debug.error(
                    _F('Invalid valid_bits for picc_select. rx_valid_bits: {}', rx_valid_bits))
            return StatusCode.STATUS_INVALID, _uid

        # Prepare MFRC522
        # ValuesAfterColl=1 => Bits received after collision are cleared.
        self.pcd_clear_register_bitmask(PCD_Register.CollReg, 0x80)

        # Repeat Cascade Level loop until we have a complete UID.
        uid_complete = False
        while not uid_complete:
            if self.__log_trace:
                logger_trace.debug('>> picc_select: cascade loop iteration')
            # Set the Cascade Level in the SEL byte, find out if we need to use
            # the Cascade Tag in byte 2.
            if cascade_level == 1:
                _buffer[0] = PICC_Command.PICC_CMD_SEL_CL1.value
                uid_index = 0
                # When we know that the UID has more than 4 bytes
                use_cascade_tag = rx_valid_bits and _uid.size > 4
            elif cascade_level == 2:
                _buffer[0] = PICC_Command.PICC_CMD_SEL_CL2.value
                uid_index = 3
                # When we know that the UID has more than 7 bytes
                use_cascade_tag = rx_valid_bits and _uid.size > 7
            elif cascade_level == 3:
                _buffer[0] = PICC_Command.PICC_CMD_SEL_CL3.value
                uid_index = 6
                # Never used in CL3.
                use_cascade_tag = False
            else:
                if self.__log_debug:
                    logger_debug.error(
                        _F('Error occured in picc_select. Wrong cascade level. cascade: {}', cascade_level))
                return StatusCode.STATUS_INTERNAL_ERROR, _uid

            # How many UID bits are known in this Cascade Level?
            current_level_known_bits = rx_valid_bits - (8 * uid_index)
            if current_level_known_bits < 0:
                current_level_known_bits = 0
            # Copy the known bits from uid->uidByte[] to _buffer[]
            index = 2   # destination index in _buffer[]
            if use_cascade_tag:
                _buffer[index] = PICC_Command.PICC_CMD_CT.value
                index += 1
            # The number of bytes needed to represent the known bits for this
            # level.
            bytes_to_copy = current_level_known_bits // 8 + \
                (1 if current_level_known_bits % 8 else 0)
            if bytes_to_copy:
                # Max 4 bytes in each Cascade Level. Only 3 left if we use the
                # Cascade Tag
                max_bytes = 3 if use_cascade_tag else 4
                if bytes_to_copy > max_bytes:
                    bytes_to_copy = max_bytes
                for count in range(bytes_to_copy):
                    _buffer[index] = _uid.uid_byte[uid_index + count]
                    index += 1
            # Now that the data has been copied we need to include the 8 bits
            # in CT in currentLevelKnownBits
            if use_cascade_tag:
                current_level_known_bits += 8

            # Repeat anti collision loop until we can transmit all UID bits +
            # BCC and receive a SAK - max 32 iterations.
            select_done = False
            while not select_done:
                if self.__log_trace:
                    logger_trace.debug(
                        '>> picc_select: cascade loop iteration: anti collision loop iteration')
                # Find out how many bits and bytes to send and receive.
                # All UID bits in this Cascade Level are known. This is a
                # SELECT.
                if current_level_known_bits >= 32:
                    if self.__log_trace:
                        logger_trace.debug(
                            _F('>> picc_select: cascade loop iteration: anti collision loop iteration: all UID bits ({}) in cascade level are known --> SELECT', current_level_known_bits))
                    # Serial.print(F("SELECT: currentLevelKnownBits=")); Serial.println(currentLevelKnownBits, DEC);
                    # NVB - Number of Valid Bits: Seven whole bytes
                    _buffer[1] = 0x70
                    # Calculate BCC - Block Check Character
                    _buffer[6] = _buffer[2] ^ _buffer[3] ^ _buffer[4] ^ _buffer[5]
                    # Calculate CRC_A
                    # PCD_CalculateCRC(_buffer, 7, &_buffer[7]);
                    status, crc_result = self.pcd_calulate_crc(_buffer[:7])
                    if status != StatusCode.STATUS_OK:
                        if self.__log_debug:
                            logger_debug.error(
                                _F('Error occured in picc_select anti collision loop. Calculation of CRC_A not OK: {}', status.name))
                        return status, _uid
                    _buffer[7] = crc_result[0]
                    _buffer[8] = crc_result[1]
                    tx_last_bits = 0  # 0 => All 8 bits are valid.
                    buffer_used = 9
                    # Store response in the last 3 bytes of _buffer (BCC and
                    # CRC_A - not needed after tx)
                    response_buffer_index = 6
                    response_length = 3
                else:   # This is an ANTICOLLISION.
                    if self.__log_trace:
                        logger_trace.debug(
                            _F('>> picc_select: cascade loop iteration: anti collision loop iteration: (current_level_known_bits={}) --> ANTICOLLISION', current_level_known_bits))
                    # Serial.print(F("ANTICOLLISION: currentLevelKnownBits=")); Serial.println(currentLevelKnownBits, DEC);
                    tx_last_bits = current_level_known_bits % 8
                    # Number of whole bytes in the UID part.
                    count = current_level_known_bits // 8
                    index = 2 + count                        # Number of whole bytes: SEL + NVB + UIDs
                    # NVB - Number of Valid Bits
                    _buffer[1] = (index << 4) + tx_last_bits
                    buffer_used = index + (1 if tx_last_bits else 0)
                    # Store response in the unused part of _buffer
                    response_buffer_index = index
                    response_length = len(_buffer) - index

                # Set bit adjustments
                # Having a separate variable is overkill. But it makes the next
                # line easier to read.
                rx_align = tx_last_bits
                # RxAlign = BitFramingReg[6..4]. TxLastBits =
                # BitFramingReg[2..0]
                self.pcd_write_register(
                    PCD_Register.BitFramingReg, (rx_align << 4) + tx_last_bits)

                # Transmit the _buffer and receive the response.
                status, _rx_back_data, _rx_valid_bits = self.pcd_transceive_data(
                    _buffer[:buffer_used], True, tx_last_bits, rx_align)
                if _rx_back_data:
                    if self.__log_trace:
                        logger_trace.debug(_F('>> picc_select: cascade loop iteration: anti collision loop iteration: copy data. data: [{}], buffer_index: {}', format_hex(
                            _rx_back_data), response_buffer_index))
                    # copy _rx_back_data into _buffer starting from
                    # response_buffer_index
                    for i in range(len(_rx_back_data)):
                        _buffer[response_buffer_index + i] = _rx_back_data[i]
                else:
                    if self.__log_debug:
                        logger_debug.warn(_F('No back data received from transceive_data in picc_select anti collision loop. buffer: [{}], used: {}, tx_last_bits: {}, rx_align: {}', format_hex(
                            _buffer), buffer_used, tx_last_bits, rx_align))

                # More than one PICC in the field => collision.
                if status == StatusCode.STATUS_COLLISION:
                    if self.__log_trace:
                        logger_trace.debug(
                            '>> picc_select: cascade loop iteration: anti collision loop iteration: more than one PICC in field --> collision')
                    # CollReg[7..0] bits are: ValuesAfterColl reserved
                    # CollPosNotValid CollPos[4:0]
                    value_of_col_reg = self.pcd_read_register(
                        PCD_Register.CollReg)
                    if value_of_col_reg & 0x20:                                             # CollPosNotValid
                        if self.__log_debug:
                            logger_debug.error(
                                'Error occured in picc_select anti collision loop. Invalid collision position')
                        # Without a valid collision position we cannot continue
                        return StatusCode.STATUS_COLLISION, _uid
                    # Values 0-31, 0 means bit 32.
                    collision_pos = value_of_col_reg & 0x1F
                    if collision_pos == 0:
                        collision_pos = 32
                    if collision_pos <= current_level_known_bits:                          # No progress - should not happen
                        if self.__log_debug:
                            logger_debug.error(
                                _F('Error occured in picc_select anti collision loop. No progress collision_pos ({}) < current_level_known_bits ({})', collision_pos, current_level_known_bits))
                        return StatusCode.STATUS_INTERNAL_ERROR, _uid
                    # Choose the PICC with the bit set.
                    current_level_known_bits = collision_pos
                    # The bit to modify
                    count = current_level_known_bits % 8
                    check_bit = (current_level_known_bits - 1) % 8
                    # First byte is index 0.
                    index = 1 + (current_level_known_bits // 8) + \
                        (1 if count else 0)
                    _buffer[index] |= (1 << check_bit)
                elif status != StatusCode.STATUS_OK:
                    if self.__log_debug:
                        logger_debug.error(
                            _F('Error occured in picc_select anti collision loop. pcd_transceive_data returned NOT OK ({})', status.name))
                    return status, _uid
                else:                                                                       # STATUS_OK
                    if self.__log_trace:
                        logger_trace.debug(
                            '>> picc_select: cascade loop iteration: anti collision loop iteration: status OK')
                    # This was a SELECT.
                    if current_level_known_bits >= 32:
                        # No more anticollision
                        select_done = True
                        # We continue below outside the while.
                    # This was an ANTICOLLISION.
                    else:
                        # We now have all 32 bits of the UID in this Cascade
                        # Level
                        current_level_known_bits = 32
                        # Run loop again to do the SELECT.
            # End of while (!selectDone)

            # We do not check the CBB - it was constructed by us above.

            # Copy the found UID bytes from _buffer[] to uid->uidByte[]
            # source index in _buffer[]
            index = 3 if _buffer[2] == PICC_Command.PICC_CMD_CT.value else 2
            bytes_to_copy = 3 if _buffer[2] == PICC_Command.PICC_CMD_CT.value else 4
            for count in range(bytes_to_copy):
                _uid.uid_byte[uid_index + count] = _buffer[index]
                index += 1

            if self.__log_trace:
                logger_trace.debug(
                    '>> picc_select: cascade loop iteration: check response SAK and verify CRC_A')

            # Check response SAK (Select Acknowledge)
            # SAK must be exactly 24 bits (1 byte + CRC_A).
            if response_length != 3 or tx_last_bits != 0:
                if self.__log_debug:
                    logger_debug.error(
                        _F('Error occured in picc_select cascade loop. Response SAK (Select Acknowledge) is not exactly 24 bits (SAK bits: {}, SAK valid last bits: {})', response_length * 8, tx_last_bits))
                return StatusCode.STATUS_ERROR, _uid
            # Verify CRC_A - do our own calculation and store the control in
            # _buffer[2..3] - those bytes are not needed anymore.
            status, crc_result = self.pcd_calulate_crc(
                _rx_back_data[:1])  # responseBuffer, 1, &_buffer[2]);
            if status != StatusCode.STATUS_OK:
                if self.__log_debug:
                    logger_debug.error(
                        _F('Error occured in picc_select cascade loop. CRC_A calculation returned NOT OK ({})', status.name))
                return status, _uid
            _buffer[2] = crc_result[0]
            _buffer[3] = crc_result[1]
            if ((_buffer[2] != _buffer[response_buffer_index + 1]) or (_buffer[3] != _buffer[response_buffer_index + 2])):
                if self.__log_debug:
                    logger_debug.error(
                        'Error occured in picc_select cascade loop. Wrong CRC_A')
                return StatusCode.STATUS_CRC_WRONG, _uid
            # Cascade bit set - UID not complete yes
            if (_buffer[response_buffer_index] & 0x04):
                cascade_level += 1
            else:
                uid_complete = True
                _uid.sak = _buffer[response_buffer_index]
        # End of while (!uidComplete)

        # Set correct uid->size
        _uid.size = 3 * cascade_level + 1

        if self.__log_trace:
            logger_trace.debug(
                _F('>> picc_select: cascade loop finished: uid: [{}]', format_hex(_uid.uid())))

        return StatusCode.STATUS_OK, _uid
    # End PICC_Select()

    def picc_halt_a(self):
        '''
        Instructs a PICC in state ACTIVE(*) to go to state HALT.

        @return: StatusCode
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_halt_a')

        # Build command buffer
        _buffer = []
        _buffer.append(PICC_Command.PICC_CMD_HLTA.value)
        _buffer.append(0)

        # Calculate CRC_A
        result, crc_result = self.pcd_calulate_crc(_buffer)
        if result != StatusCode.STATUS_OK:
            return result

        # Send the command.
        # The standard says:
        #        If the PICC responds with any modulation during a period of 1 ms after the end of the frame containing the
        #        HLTA command, this response shall be interpreted as 'not acknowledge'.
        # We interpret that this way: Only STATUS_TIMEOUT is a success.
        result = self.pcd_transceive_data(_buffer + crc_result, False, 0)
        if result == StatusCode.STATUS_TIMEOUT:
            return StatusCode.STATUS_OK
        if result == StatusCode.STATUS_OK:     # That is ironically NOT ok in this case ;-)
            return StatusCode.STATUS_ERROR
        return result

    #=========================================================================
    # Functions for communicating with MIFARE PICCs
    #=========================================================================

    def pcd_authenticate(self, command, block_addr, key, uid):
        '''
        Executes the MFRC522 MFAuthent command.
        This command manages MIFARE authentication to enable a secure communication to any MIFARE Mini, MIFARE 1K and MIFARE 4K card.
        The authentication is described in the MFRC522 datasheet section 10.3.1.9 and http://www.nxp.com/documents/data_sheet/MF1S503x.pdf section 10.1.
        For use with MIFARE Classic PICCs.
        The PICC must be selected - ie in state ACTIVE(*) - before calling this function.
        Remember to call PCD_StopCrypto1() after communicating with the authenticated PICC - otherwise no new communications can start.

        All keys are set to FFFFFFFFFFFFh at chip delivery.

        @param command: PICC_CMD_MF_AUTH_KEY_A or PICC_CMD_MF_AUTH_KEY_B
        @param block_addr: The block number. See numbering in the comments in the .h file.
        @param key: MIFARE_Key containing the Crypteo1 key to use (6 bytes)
        @param uid: Uid struct. The first 4 bytes of the UID is used.
        @return: STATUS_OK on success, STATUS_??? otherwise. Probably STATUS_TIMEOUT if you supply the wrong key.
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_authenticate')

        wait_irq = 0x10        # IdleIRq

        # Build command buffer
        send_data = [0] * 12
        send_data[0] = command.value
        send_data[1] = block_addr
        for i in range(MIFARE_Misc.MF_KEY_SIZE.value):   # 6 key bytes
            send_data[2 + i] = key.key_byte[i]
        # Use the last uid bytes as specified in http://cache.nxp.com/documents/application_note/AN10927.pdf
        # section 3.2.5 "MIFARE Classic Authentication".
        # The only missed case is the MF1Sxxxx shortcut activation,
        # but it requires cascade tag (CT) byte, that is not part of uid.
        for i in range(4):                              # The last 4 bytes of the UID
            send_data[8 + i] = uid.uid_byte[i + uid.size - 4]

        # Start the authentication.
        status, __, __ = self.pcd_communicate_with_picc(
            PCD_Command.PCD_MFAuthent, wait_irq, send_data, False, 0)
        return status

    def pcd_stop_crypto1(self):
        '''
        Used to exit the PCD from its authenticated state.
        Remember to call this function after communicating with an authenticated PICC - otherwise no new communications can start.
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_stop_crypto1')

        # Clear MFCrypto1On bit
        # Status2Reg[7..0] bits are: TempSensClear I2CForceHS reserved reserved
        # MFCrypto1On ModemState[2:0]
        self.pcd_clear_register_bitmask(PCD_Register.Status2Reg, 0x08)

    def mifare_read(self, block_addr):
        '''
        Reads 16 bytes (+ 2 bytes CRC_A) from the active PICC.

        For MIFARE Classic the sector containing the block must be authenticated before calling this function.

        For MIFARE Ultralight only addresses 00h to 0Fh are decoded.
        The MF0ICU1 returns a NAK for higher addresses.
        The MF0ICU1 responds to the READ command by sending 16 bytes starting from the page address defined by the command argument.
        For example; if blockAddr is 03h then pages 03h, 04h, 05h, 06h are returned.
        A roll-back is implemented: If blockAddr is 0Eh, then the contents of pages 0Eh, 0Fh, 00h and 01h are returned.

        The buffer must be at least 18 bytes because a CRC_A is also returned.
        Checks the CRC_A before returning STATUS_OK.

        @return: (StatusCode, data) - Status and data read from the given block address
        '''
        if self.__log_trace:
            logger_trace.debug('>> mifare_read')

        # Build command buffer
        _buffer = []
        _buffer.append(PICC_Command.PICC_CMD_MF_READ.value)
        _buffer.append(block_addr)
        # Calculate CRC_A
        result, crc_result = self.pcd_calulate_crc(_buffer)
        if result != StatusCode.STATUS_OK:
            return result

        # Transmit the buffer and receive the response, validate CRC_A.
        status, data, __ = self.pcd_transceive_data(
            _buffer + crc_result, True, 0, 0, True)
        return status, data

    def mifare_write(self, block_addr, data):
        '''
        Writes 16 bytes to the active PICC.

        For MIFARE Classic the sector containing the block must be authenticated before calling this function.

        For MIFARE Ultralight the operation is called "COMPATIBILITY WRITE".
        Even though 16 bytes are transferred to the Ultralight PICC, only the least significant 4 bytes (bytes 0 to 3)
        are written to the specified address. It is recommended to set the remaining bytes 04h to 0Fh to all logic 0.

        @param block_addr: MIFARE Classic: The block (0-0xff) number. MIFARE Ultralight: The page (2-15) to write to.
        @param data: The 16 bytes to write to the PICC
        @return STATUS_OK on success, STATUS_??? otherwise.
        '''
        if self.__log_trace:
            logger_trace.debug('>> mifare_write')

        # Sanity check
        if not data or len(data) < 16:
            if self.__log_debug:
                logger_debug.error(_F('Invalid number of bytes (< 16) for mifare_write. Data (n={}): [{}]', len(
                    data), format_hex(data)))
            return StatusCode.STATUS_INVALID

        # Mifare Classic protocol requires two communications to perform a write.
        # Step 1: Tell the PICC we want to write to block blockAddr.
        _cmd_buffer = []
        _cmd_buffer.append(PICC_Command.PICC_CMD_MF_WRITE.value)
        _cmd_buffer.append(block_addr)
        # Adds CRC_A and checks that the response is MF_ACK.
        result = self.pcd_mifare_transceive(_cmd_buffer)
        if result != StatusCode.STATUS_OK:
            return result

        # Step 2: Transfer the data
        # Adds CRC_A and checks that the response is MF_ACK.
        result = self.pcd_mifare_transceive(data)
        if result != StatusCode.STATUS_OK:
            return result

        return StatusCode.STATUS_OK

    def mifare_ultralight_write(self, page, data):
        '''
        Writes a 4 byte page to the active MIFARE Ultralight PICC.

        @param page: The page (2-15) to write to.
        @param data: The 4 bytes to write to the PICC
        @return STATUS_OK on success, STATUS_??? otherwise.
        '''
        if self.__log_trace:
            logger_trace.debug('>> mifare_ultralight_write')

        # Sanity check
        if not data or len(data) < 4:
            return StatusCode.STATUS_INVALID

        # Build commmand buffer
        _cmd_buffer = []
        _cmd_buffer.append(PICC_Command.PICC_CMD_UL_WRITE.value)
        _cmd_buffer.append(page)
        _cmd_buffer += data[:4]

        # Perform the write
        # Adds CRC_A and checks that the response is MF_ACK.
        result = self.pcd_mifare_transceive(_cmd_buffer)
        if result != StatusCode.STATUS_OK:
            return result

        return StatusCode.STATUS_OK

    def mifare_decrement(self, block_addr, delta):
        '''
        MIFARE Decrement subtracts the delta from the value of the addressed block, and stores the result in a volatile memory.
        For MIFARE Classic only. The sector containing the block must be authenticated before calling this function.
        Only for blocks in "value block" mode, ie with access bits [C1 C2 C3] = [110] or [001].
        Use MIFARE_Transfer() to store the result in a block.

        @param block_addr: The block (0-0xff) number.
        @param delta: This number is subtracted from the value of block blockAddr.
        @return: STATUS_OK on success, STATUS_??? otherwise.
        '''
        if self.__log_trace:
            logger_trace.debug('>> mifare_decrement')

        return self._mifare_two_step_helper(PICC_Command.PICC_CMD_MF_DECREMENT, block_addr, delta)

    def mifare_increment(self, block_addr, delta):
        '''
        MIFARE Increment adds the delta to the value of the addressed block, and stores the result in a volatile memory.
        For MIFARE Classic only. The sector containing the block must be authenticated before calling this function.
        Only for blocks in "value block" mode, ie with access bits [C1 C2 C3] = [110] or [001].
        Use MIFARE_Transfer() to store the result in a block.

        @param block_addr: The block (0-0xff) number.
        @param delta: This number is added to the value of block blockAddr.
        @return: STATUS_OK on success, STATUS_??? otherwise.
        '''
        if self.__log_trace:
            logger_trace.debug('>> mifare_increment')

        return self._mifare_two_step_helper(PICC_Command.PICC_CMD_MF_INCREMENT, block_addr, delta)

    def mifare_restore(self, block_addr):
        '''
        MIFARE Restore copies the value of the addressed block into a volatile memory.
        For MIFARE Classic only. The sector containing the block must be authenticated before calling this function.
        Only for blocks in "value block" mode, ie with access bits [C1 C2 C3] = [110] or [001].
        Use MIFARE_Transfer() to store the result in a block.

        @param block_addr: The block (0-0xff) number.
        @return: STATUS_OK on success, STATUS_??? otherwise.
        '''
        if self.__log_trace:
            logger_trace.debug('>> mifare_restore')

        # The datasheet describes Restore as a two step operation, but does not explain what data to transfer in step 2.
        # Doing only a single step does not work, so I chose to transfer 0L in
        # step two.
        return self._mifare_two_step_helper(PICC_Command.PICC_CMD_MF_RESTORE, block_addr, 0)

    def _mifare_two_step_helper(self, command, block_addr, data):
        '''
        Helper function for the two-step MIFARE Classic protocol operations Decrement, Increment and Restore.

        @param command: The command to use
        @param block_addr: The block (0-0xff) number.
        @param data: The data to transfer in step 2
        @return: STATUS_OK on success, STATUS_??? otherwise.
        '''
        if self.__log_trace:
            logger_trace.debug('>> mifare_two_step_helper')

        # Step 1: Tell the PICC the command and block address
        _cmd_buffer = []
        _cmd_buffer.append(command.value)
        _cmd_buffer.append(block_addr)
        # Adds CRC_A and checks that the response is MF_ACK.
        result = self.pcd_mifare_transceive(_cmd_buffer)
        if result != StatusCode.STATUS_OK:
            return result

        # Step 2: Transfer the data
        # Adds CRC_A and accept timeout as success.
        result = self.pcd_mifare_transceive(data, True)
        if result != StatusCode.STATUS_OK:
            return result

        return StatusCode.STATUS_OK

    def mifare_transfer(self, block_addr):
        '''
        MIFARE Transfer writes the value stored in the volatile memory into one MIFARE Classic block.
        For MIFARE Classic only. The sector containing the block must be authenticated before calling this function.
        Only for blocks in "value block" mode, ie with access bits [C1 C2 C3] = [110] or [001].

        @param block_addr: The block (0-0xff) number.
        @return STATUS_OK on success, STATUS_??? otherwise.
        '''
        if self.__log_trace:
            logger_trace.debug('>> mifare_transfer')

        _cmd_buffer = []                # We only need room for 2 bytes.

        # Tell the PICC we want to transfer the result into block blockAddr.
        _cmd_buffer.append(PICC_Command.PICC_CMD_MF_TRANSFER.value)
        _cmd_buffer.append(block_addr)
        # Adds CRC_A and checks that the response is MF_ACK.
        result = self.pcd_mifare_transceive(_cmd_buffer)
        if result != StatusCode.STATUS_OK:
            return result
        return StatusCode.STATUS_OK

    def mifare_get_value(self, block_addr):
        '''
        Helper routine to read the current value from a Value Block.

        Only for MIFARE Classic and only for blocks in "value block" mode, that
        is: with access bits [C1 C2 C3] = [110] or [001]. The sector containing
        the block must be authenticated before calling this function. 

        @param block_addr: The block (0x00-0xff) number.
        @param[out]  value       Current value of the Value Block.
        @return: (StatusCode, value) - value contains the current value of the Value Block.
        '''
        if self.__log_trace:
            logger_trace.debug('>> mifare_get_value')

        # Read the block
        status, data = self.mifare_read(block_addr)
        if status == StatusCode.STATUS_OK:
            # Extract the value
            value = (data[3] << 24) | (
                data[2] << 16) | (data[1] << 8) | data[0]
            return StatusCode.STATUS_OK, value
        return status, None

    def mifare_set_value(self, block_addr, value):
        '''
        Helper routine to write a specific value into a Value Block.

        Only for MIFARE Classic and only for blocks in "value block" mode, that
        is: with access bits [C1 C2 C3] = [110] or [001]. The sector containing
        the block must be authenticated before calling this function. 

        @param block_addre: The block (0x00-0xff) number.
        @param value: New value of the Value Block.
        @return: STATUS_OK on success, STATUS_??? otherwise.
        '''
        if self.__log_trace:
            logger_trace.debug('>> mifare_set_value')

        # Translate the int32_t into 4 bytes; repeated 2x in value block
        _buffer = [0] * 16
        _buffer[0] = _buffer[8] = (value & 0xFF)
        _buffer[1] = _buffer[9] = (value & 0xFF00) >> 8
        _buffer[2] = _buffer[10] = (value & 0xFF0000) >> 16
        _buffer[3] = _buffer[11] = (value & 0xFF000000) >> 24
        # Inverse 4 bytes also found in value block
        _buffer[4] = ~_buffer[0]
        _buffer[5] = ~_buffer[1]
        _buffer[6] = ~_buffer[2]
        _buffer[7] = ~_buffer[3]
        # Address 2x with inverse address 2x
        _buffer[12] = _buffer[14] = block_addr
        _buffer[13] = _buffer[15] = ~block_addr

        # Write the whole data block
        return self.mifare_write(block_addr, _buffer)

    # TODO missing function: MFRC522::StatusCode
    # MFRC522::PCD_NTAG216_AUTH(byte* passWord, byte pACK[]) //Authenticate
    # with 32bit password

    #=========================================================================
    # Support functions
    #=========================================================================

    def pcd_mifare_transceive(self, send_data, accept_timeout=False):
        '''
        Wrapper for MIFARE protocol communication.
        Adds CRC_A, executes the Transceive command and checks that the response is MF_ACK or a timeout.

        @param send_data: Data to transfer to the FIFO. Do NOT include the CRC_A.
        @param accept_timeout: True => A timeout is also success
        @return STATUS_OK on success, STATUS_??? otherwise.
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_mifare_transceive')

        # We need room for 16 bytes data and 2 bytes CRC_A.
        _cmd_buffer = [0] * 18

        # Sanity check
        if not send_data or len(send_data) > 16:
            return StatusCode.STATUS_INVALID

        # Copy sendData[] to cmdBuffer[] and add CRC_A
        #memcpy(cmdBuffer, sendData, sendLen);
        result, crc_result = self.pcd_calulate_crc(send_data)
        if result != StatusCode.STATUS_OK:
            return result

        # Transceive the data, store the reply in cmdBuffer[]
        wait_irq = 0x30  # RxIRq and IdleIRq
        result, rx_back_data, rx_valid_bits = self.pcd_communicate_with_picc(
            PCD_Command.PCD_Transceive, wait_irq, send_data + crc_result, True, 0)
        if accept_timeout and result == StatusCode.STATUS_TIMEOUT:
            return StatusCode.STATUS_OK
        if result != StatusCode.STATUS_OK:
            return result
        # The PICC must reply with a 4 bit ACK
        if len(rx_back_data) != 1 or rx_valid_bits != 4:
            if self.__log_debug:
                logger_debug.error(
                    'Invalid ACK received from PICC in mifare transceive')
            return StatusCode.STATUS_ERROR
        if rx_back_data[0] != MIFARE_Misc.MF_ACK.value:
            if self.__log_debug:
                logger_debug.warn(
                    'Received NAK from PICC in mifare transceive')
            return StatusCode.STATUS_MIFARE_NACK
        return StatusCode.STATUS_OK

    def get_status_code_name(self, code):
        '''
        Returns a __FlashStringHelper pointer to a status code name.

        @param code: One of the StatusCode enums.
        @return:  StatusCode name
        '''
        return code.get_name()

    def picc_get_type(self, uid):
        '''
        Translates the SAK (Select Acknowledge) from the UID to a PICC type.

        @param sak: The SAK byte returned from PICC_Select().
        @return: PICC_Type
        '''
        return uid.get_picc_type()

    def picc_get_type_name(self, picc_type):
        '''
        Returns a __FlashStringHelper pointer to the PICC type name.

        @param picc_type: One of the PICC_Type enums.
        @return: PICC_Type name
        '''
        return picc_type.get_name()

    def pcd_get_version_name(self, version):
        # Lookup which version
        if version == 0x88:
            return '(clone)'
        elif version == 0x90:
            return 'v0.0'
        elif version == 0x91:
            return 'v1.0'
        elif version == 0x92:
            return 'v2.0'
        elif version == 0x12:
            return 'counterfeit chip'
        else:
            return '(unknown)'

    def pcd_dump_version_to_serial(self):
        '''
        Dumps debug info about the connected PCD to Serial.
        Shows all known firmware versions
        '''
        if self.__log_trace:
            logger_trace.debug('>> pcd_dump_version_to_serial')

        # Get the MFRC522 firmware version
        v = self.pcd_read_register(PCD_Register.VersionReg)
        print('Firmware Version: {:#x} = {}'.format(
            v, self.pcd_get_version_name(v)))
        # When 0x00 or 0xFF is returned, communication probably failed
        if (v == 0x00) or (v == 0xFF):
            print('WARNING: Communication failure, is the MFRC522 properly connected?')

    def picc_dump_to_serial(self, uid):
        '''
        Dumps debug info about the selected PICC to Serial.
        On success the PICC is halted after dumping the data.
        For MIFARE Classic the factory default key of 0xFFFFFFFFFFFF is tried.  

        @param uid: Pointer to Uid struct returned from a successful PICC_Select().
        @deprecated: Kept for bakward compatibility
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_dump_to_serial')

        key = MIFARE_Key()

        # Dump UID, SAK and Type
        self.picc_dump_details_to_serial(uid)

        # Dump contents
        picc_type = uid.get_picc_type()
        if (picc_type == PICC_Type.PICC_TYPE_MIFARE_MINI
                or picc_type == PICC_Type.PICC_TYPE_MIFARE_1K
                or picc_type == PICC_Type.PICC_TYPE_MIFARE_4K):
            # All keys are set to FFFFFFFFFFFFh at chip delivery from the
            # factory.
            for i in range(6):
                key.key_byte[i] = 0xFF
            self.picc_dump_mifare_classic_to_serial(uid, picc_type, key)
        elif picc_type == PICC_Type.PICC_TYPE_MIFARE_UL:
            self.picc_dump_mifare_ultralight_to_serial()
        elif (picc_type == PICC_Type.PICC_TYPE_ISO_14443_4
                or picc_type == PICC_Type.PICC_TYPE_MIFARE_DESFIRE
                or picc_type == PICC_Type.PICC_TYPE_ISO_18092
                or picc_type == PICC_Type.PICC_TYPE_MIFARE_PLUS
                or picc_type == PICC_Type.PICC_TYPE_TNP3XXX):
            print('Dumping memory contents not implemented for that PICC type.')
        else:
            # No memory dump here
            pass

        # Already done if it was a MIFARE Classic PICC.
        self.picc_halt_a()

    def picc_dump_details_to_serial(self, uid):
        '''
        Dumps card info (UID,SAK,Type) about the selected PICC to Serial.

        @param uid: Pointer to Uid struct returned from a successful PICC_Select().
        @deprecated: kept for backward compatibility
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_dump_details_to_serial')

        # UID
        print('Card UID:     [{}]'.format(format_hex(uid.uid())))

        # SAK
        print('Card SAK:     {:#04x}'.format(uid.sak))

        # (suggested) PICC type
        picc_type = uid.get_picc_type()
        print('PICC type:    {}'.format(self.picc_get_type_name(picc_type)))

    def picc_dump_mifare_classic_to_serial(self, uid, picc_type, key):
        '''
        Dumps memory contents of a MIFARE Classic PICC.
        On success the PICC is halted after dumping the data.

        @param uid: Pointer to Uid struct returned from a successful PICC_Select().
        @param picc_type: One of the PICC_Type enums.
        @param key: MIFARE_Key A used for all sectors.
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_dump_mifare_classic_to_serial')

        no_of_sectors = 0
        if picc_type == PICC_Type.PICC_TYPE_MIFARE_MINI:
            # Has 5 sectors * 4 blocks/sector * 16 bytes/block = 320 bytes.
            no_of_sectors = 5
        elif picc_type == PICC_Type.PICC_TYPE_MIFARE_1K:
            # Has 16 sectors * 4 blocks/sector * 16 bytes/block = 1024 bytes.
            no_of_sectors = 16
        elif picc_type == PICC_Type.PICC_TYPE_MIFARE_4K:
            # Has (32 sectors * 4 blocks/sector + 8 sectors * 16 blocks/sector)
            # * 16 bytes/block = 4096 bytes.
            no_of_sectors = 40
        else:
            # Should not happen. Ignore.
            pass

        # Dump sectors, highest address first.
        if no_of_sectors > 0:
            print('Sector Block     0    1    2    3    4    5    6    7    8    9   10   11   12   13   14   15  AccessBits')
            for i in range(no_of_sectors):
                self.picc_dump_mifare_classic_sector_to_serial(uid, key, i)

        # Halt the PICC before stopping the encrypted session.
        self.picc_halt_a()
        self.pcd_stop_crypto1()

    def picc_dump_mifare_classic_sector_to_serial(self, uid, key, sector):
        '''
        Dumps memory contents of a sector of a MIFARE Classic PICC.
        Uses PCD_Authenticate(), MIFARE_Read() and PCD_StopCrypto1.
        Always uses PICC_CMD_MF_AUTH_KEY_A because only Key A can always read the sector trailer access bits.

        @param uid: Pointer to Uid struct returned from a successful PICC_Select().
        @param key: MIFARE_Key A for the sector.
        @param sector: sector to dump, 0..39.
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_dump_mifare_classic_sector_to_serial')

        # Address of lowest address to dump actually last block dumped)
        first_block = 0
        # Number of blocks in sector
        no_of_blocks = 0

        # The access bits are stored in a peculiar fashion.
        # There are four groups:
        #        g[3]    Access bits for the sector trailer, block 3 (for sectors 0-31) or block 15 (for sectors 32-39)
        #        g[2]    Access bits for block 2 (for sectors 0-31) or blocks 10-14 (for sectors 32-39)
        #        g[1]    Access bits for block 1 (for sectors 0-31) or blocks 5-9 (for sectors 32-39)
        #        g[0]    Access bits for block 0 (for sectors 0-31) or blocks 0-4 (for sectors 32-39)
        # Each group has access bits [C1 C2 C3]. In this code C1 is MSB and C3 is LSB.
        # The four CX bits are stored together in a nible cx and an inverted
        # nible cx_.

        # byte c1_, c2_, c3_;        # Inverted nibbles
        g = [0] * 4                # Access bits for each of the four groups.
        # byte group;               # 0-3 - active group for access bits
        # bool firstInGroup;        # True for the first block dumped in the
        # group

        # Determine position and size of sector.
        if sector < 32:                             # Sectors 0..31 has 4 blocks each
            no_of_blocks = 4
            first_block = sector * no_of_blocks
        elif sector < 40:                           # Sectors 32-39 has 16 blocks each
            no_of_blocks = 16
            first_block = 128 + (sector - 32) * no_of_blocks
        # Illegal input, no MIFARE Classic PICC has more than 40 sectors.
        else:
            return

        # Establish encrypted communications before reading the first block
        status = self.pcd_authenticate(
            PICC_Command.PICC_CMD_MF_AUTH_KEY_A, first_block, key, uid)
        if status != StatusCode.STATUS_OK:
            print('PCD_Authenticate() failed: ')
            print(self.get_status_code_name(status))
            return

        # Dump blocks, highest address first.
        block_addr = None
        # Set to true while handling the "last" (ie highest address) in the
        # sector.
        is_sector_trailer = True
        inverted_error = False      # True if one of the inverted nibbles did not match
        # for (int8_t blockOffset = no_of_blocks - 1; blockOffset >= 0;
        # blockOffset--) {
        for block_offset in range(no_of_blocks - 1, -1, -1):
            block_addr = first_block + block_offset

            # Read block
            # MIFARE_Read(blockAddr, buffer, &byteCount);
            status, data = self.mifare_read(block_addr)
            if status != StatusCode.STATUS_OK:
                print('MIFARE_Read() failed: {}'.format(
                    self.get_status_code_name(status)))
                continue

            # Parse sector trailer data
            if is_sector_trailer:
                c1 = data[7] >> 4
                c2 = data[8] & 0xF
                c3 = data[8] >> 4
                c1_ = data[6] & 0xF
                c2_ = data[6] >> 4
                c3_ = data[7] & 0xF
                inverted_error = (c1 != (~c1_ & 0xF)) or (
                    c2 != (~c2_ & 0xF)) or (c3 != (~c3_ & 0xF))
                g[0] = ((c1 & 1) << 2) | ((c2 & 1) << 1) | ((c3 & 1) << 0)
                g[1] = ((c1 & 2) << 1) | ((c2 & 2) << 0) | ((c3 & 2) >> 1)
                g[2] = ((c1 & 4) << 0) | ((c2 & 4) >> 1) | ((c3 & 4) >> 2)
                g[3] = ((c1 & 8) >> 1) | ((c2 & 8) >> 2) | ((c3 & 8) >> 3)
                is_sector_trailer = False
                _sector = sector
            else:
                _sector = ''

            # Which access group is this block in?
            if no_of_blocks == 4:
                group = block_offset
                first_in_group = True
            else:
                group = block_offset // 5
                first_in_group = (group == 3) or (
                    group != (block_offset + 1) // 5)

            if first_in_group:
                # Print access bits
                accessbits = '[{} {} {}] {} '.format((g[group] >> 2) & 1, (g[group] >> 1) & 1, (
                    g[group] >> 0) & 1, ' Inverted access bits did not match! ' if inverted_error else '')
            else:
                accessbits = ''

            # Not a sector trailer, a value block
            if (group != 3 and (g[group] == 1 or g[group] == 6)):
                value = (data[3] << 24) | (
                    data[2] << 16) | (data[1] << 8) | data[0]
                valaddr = 'Value={:#04x} Adr={:#04x} '.format(value, data[12])
            else:
                valaddr = ''

            # Dump data
            # Sector number - only on first line
            print('{sector:>6} {block:>5}  {vals}  {accessbits}{valaddr}'.format(
                sector=_sector,
                block=block_addr,
                vals=format_hex(data[:16]),
                accessbits=accessbits,
                valaddr=valaddr))

        # End PICC_DumpMifareClassicSectorToSerial()

    def picc_dump_mifare_ultralight_to_serial(self):
        '''
        Dumps memory contents of a MIFARE Ultralight PICC.
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_dump_mifare_ultralight_to_serial')

        print('Page     0     1     2     3')
        # Try the mpages of the original Ultralight. Ultralight C has more
        # pages.
        # Read returns data for 4 pages at a time.
        for page in range(0, 16, 4):
            # Read pages
            status, data = self.mifare_read(page)
            if status != StatusCode.STATUS_OK:
                print('MIFARE_Read() failed: ')
                print(self.get_status_code_name(status))
                break
            # Dump data
            for offset in range(4):
                i = page + offset
                start = offset * 4
                end = start + 4
                print('{page:>4}  {vals}'.format(
                    page=i, vals=format_hex(data[start:end])))

    # TODO missing functions

    #=========================================================================
    # Convenience functions - does not add extra functionality
    #=========================================================================

    def picc_is_new_card_present(self):
        '''
        Returns true if a PICC responds to PICC_CMD_REQA.
        Only "new" cards in state IDLE are invited. Sleeping cards in state HALT are ignored.

        @return: boolean
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_is_new_card_present')

        # Reset baud rates
        self.pcd_write_register(PCD_Register.TxModeReg, 0x00)
        self.pcd_write_register(PCD_Register.RxModeReg, 0x00)
        # Reset ModWidthReg
        self.pcd_write_register(PCD_Register.ModWidthReg, 0x26)

        result, __ = self.picc_request_a()
        return result == StatusCode.STATUS_OK or result == StatusCode.STATUS_COLLISION

    def picc_is_card_present(self):
        '''
        Returns true if a PICC responds to PICC_CMD_WUPA.
        Cards in state IDLE or HALT are invited. 

        @return: boolean
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_is_new_card_present')

        # Reset baud rates
        self.pcd_write_register(PCD_Register.TxModeReg, 0x00)
        self.pcd_write_register(PCD_Register.RxModeReg, 0x00)
        # Reset ModWidthReg
        self.pcd_write_register(PCD_Register.ModWidthReg, 0x26)

        result, __ = self.picc_wakeup_a()
        return result == StatusCode.STATUS_OK or result == StatusCode.STATUS_COLLISION

    def picc_read_card_serial(self):
        '''
        Simple wrapper around PICC_Select.
        Returns true if a UID could be read.
        Remember to call PICC_IsNewCardPresent(), PICC_RequestA() or PICC_WakeupA() first.
        The read UID is available in the class variable uid.

        @return: (result, Uid) - result is true if a UID could be read
        '''
        if self.__log_trace:
            logger_trace.debug('>> picc_read_card_serial')

        result, uid = self.picc_select()
        return result == StatusCode.STATUS_OK, uid


#=========================================================================
# Helper functions for the python version of MFRC522
#=========================================================================


# Helper function to suspend executen for x microsecends
def usleep(x): return sleep(x / 1000000.0)
