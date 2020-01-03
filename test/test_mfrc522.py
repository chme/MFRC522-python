'''
Created on Jan 14, 2019

@author: asiate
'''
import logging
import sys
import unittest

import unittest.mock as mock


# Mock RPi.GPIO and spidev
sys.modules['RPi'] = mock.MagicMock()
sys.modules['RPi.GPIO'] = mock.MagicMock()
sys.modules['spidev'] = mock.MagicMock()

# After mocking libraries import the system under test (sut)
from mfrc522 import MFRC522
from mfrc522 import PCD_Firmware


class TestMFRC522(unittest.TestCase):

    def setUp(self):
        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.logger = logging.getLogger('mfrc522.log')
        self.logger.addHandler(self.stream_handler)

    def tearDown(self):
        self.logger.removeHandler(self.stream_handler)

    def test__spi_transfer(self):
        # arrange
        sut = MFRC522()
        sut.spi.xfer2 = mock.MagicMock(return_value=[125, 6, 6, 0])
        data = [1, 2, 3]

        # act
        actual = sut._spi_transfer(data)

        # assert
        self.assertEqual(actual, [125, 6, 6, 0])

    def test__pcd_get_firmware_version(self):
        # arrange
        sut = MFRC522()
        sut.spi.xfer2 = mock.MagicMock(return_value=[0, 0x88])

        # act
        actual = sut.pcd_get_firmware_version()

        # assert
        self.assertEqual(actual, PCD_Firmware.FM17522)

    def test__pcd_get_firmware_version_with_error(self):
        # arrange
        sut = MFRC522()
        sut.spi.xfer2 = mock.MagicMock(return_value=[0, 0xFF])

        # act
        actual = sut.pcd_get_firmware_version()

        # assert
        self.assertEqual(actual, PCD_Firmware.UNKNOWN)

    def test__pcd_get_firmware_version_with_unknown(self):
        # arrange
        sut = MFRC522()
        sut.spi.xfer2 = mock.MagicMock(return_value=[0, 0x42])

        # act
        actual = sut.pcd_get_firmware_version()

        # assert
        self.assertEqual(actual, PCD_Firmware.UNKNOWN)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TestMFRC522.testName']
    unittest.main()
