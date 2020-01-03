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
from mfrc522 import Uid
from mfrc522 import PICC_Type


class TestMFRC522(unittest.TestCase):

    def setUp(self):
        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.logger = logging.getLogger('mfrc522.log')
        self.logger.addHandler(self.stream_handler)

    def tearDown(self):
        self.logger.removeHandler(self.stream_handler)

    def test__get_picc_type_with_sak_none_returns_unkown(self):
        # arrange
        sut = Uid()
        sut.sak = None

        # act
        actual = sut.get_picc_type()

        # assert
        self.assertEqual(actual, PICC_Type.PICC_TYPE_UNKNOWN)

    def test__get_picc_type_with_sak_0x08_returns_mifare1k(self):
        # arrange
        sut = Uid()
        sut.sak = 0x08

        # act
        actual = sut.get_picc_type()

        # assert
        self.assertEqual(actual, PICC_Type.PICC_TYPE_MIFARE_1K)

    def test__get_picc_type_with_lsbyte_set(self):
        # arrange
        sut = Uid()
        sut.sak = 0x20 | 0x80

        # act
        actual = sut.get_picc_type()

        # assert
        self.assertEqual(actual, PICC_Type.PICC_TYPE_ISO_14443_4)

    def test__get_picc_type_with_sak_unknown_returns_unkown(self):
        # arrange
        sut = Uid()
        sut.sak = 0x42

        # act
        actual = sut.get_picc_type()

        # assert
        self.assertEqual(actual, PICC_Type.PICC_TYPE_UNKNOWN)


if __name__ == "__main__":
    unittest.main()
