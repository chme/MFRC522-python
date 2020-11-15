import logging
import sys
import unittest
import unittest.mock as mock


# Mock RPi.GPIO and spidev
sys.modules['RPi'] = mock.MagicMock()
sys.modules['RPi.GPIO'] = mock.MagicMock()
sys.modules['spidev'] = mock.MagicMock()
sys.modules['MFRC522'] = mock.MagicMock()

# After mocking libraries import the system under test (sut)
from mfrc522 import SimpleMFRC522            # noqa
from mfrc522 import StatusCode               # noqa

logging.basicConfig(level=logging.DEBUG)


class TestSimpleMFRC522(unittest.TestCase):

    def setUp(self):
        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.logger = logging.getLogger('mfrc522.log')
        self.logger.addHandler(self.stream_handler)

    def tearDown(self):
        self.logger.removeHandler(self.stream_handler)

    def test__read_text_with_cancel_irq(self):
        # arrange
        sut = SimpleMFRC522()
        sut.wait_for_interrupt = mock.MagicMock(return_value=False)

        # act
        status, uid, text = sut.read_text()

        # assert
        self.assertEqual(status, StatusCode.STATUS_CANCELED)
        self.assertEqual(uid, None)
        self.assertEqual(text, None)


if __name__ == "__main__":
    unittest.main()
