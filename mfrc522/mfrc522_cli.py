import argparse
import cmd2
import RPi.GPIO as GPIO
from .simple_mfrc522 import SimpleMFRC522
from cmd2 import style, fg, with_category
import logging


class MFRC522_Cli(cmd2.Cmd):
    CMD_CAT_MFRC = 'MFRC522'

    def __init__(self, rfid):
        super().__init__(allow_cli_args=False)

        self.intro = style('''

█▀▄▀█ █▀▀ █▀▀█ █▀▀ █▀▀ █▀█ █▀█
█░▀░█ █▀▀ █▄▄▀ █░░ ▀▀▄ ░▄▀ ░▄▀
▀░░░▀ ▀░░ ▀░▀▀ ▀▀▀ ▄▄▀ █▄▄ █▄▄

''', fg=fg.blue) + style('''
Enter command(s), to see a list of available commands enter "help -v", to exit enter "quit":

''', fg=fg.white)

        self.prompt = style('➜ ', fg=fg.green, bold=True)
        self.rfid = rfid

        # Remove shell and python shell commands
        delattr(cmd2.Cmd, 'do_shell')
        delattr(cmd2.Cmd, 'do_py')

        # Hide some other builtin commands
        self.hidden_commands.append('alias')
        self.hidden_commands.append('edit')
        self.hidden_commands.append('macro')
        self.hidden_commands.append('run_pyscript')
        self.hidden_commands.append('run_script')
        self.hidden_commands.append('shortcuts')

    @with_category(CMD_CAT_MFRC)
    def do_version(self, args):
        '''
        Read firmware version from rfid reader
        '''
        firmware = self.rfid.firmware_version()
        self.poutput('Firmware Version: {:#x} = {} - {}'.format(firmware.value, firmware.version, firmware.description))

    @with_category(CMD_CAT_MFRC)
    def do_selftest(self, args):
        '''
        Read firmware version and run selftest for supported rfid reader
        '''
        firmware = self.rfid.firmware_version()
        self.poutput('Reader firmware: {:#x} = {} - {}'.format(firmware.value, firmware.version, firmware.description))

        result = self.rfid.selftest()
        if result:
            self.poutput(style('Selftest finished successfully', fg=fg.green))
        else:
            self.perror('Selftest failed, reader is either unsupported or unknown')

    @with_category(CMD_CAT_MFRC)
    def do_check_card_present(self, args):
        '''
        Checks if a card (PICC) is present (PICC state can be IDLE or HALT)
        (Sends a PICC_CMD_WUPA and checks if a PICC responds)
        '''
        result = self.rfid.is_card_present()
        self.poutput('{}'.format('Card is present' if result else 'No cards found'))

    @with_category(CMD_CAT_MFRC)
    def do_check_new_card_present(self, args):
        '''
        Checks if a new card (PICC) is present (only PICC in state IDLE are invited)
        (Sends a PICC_CMD_REQA and checks if a PICC responds)
        '''
        result = self.rfid.is_new_card_present()
        self.poutput('{}'.format('Card found' if result else 'No cards found'))

    @with_category(CMD_CAT_MFRC)
    def do_read_uid(self, args):
        '''
        Checks if a card (PICC) is present (state IDLE or HALT), puts it into the READY state
        and transmits the SELECT/ANTICOLLISION commands to read the UID
        '''
        result = self.rfid.is_card_present()

        if not result:
            self.poutput('No card found')
            return

        result, uid = self.rfid.read_card_serial()
        if result:
            self.poutput(style('Card "{}" found with uid: {}'.format(
                uid.get_picc_type().get_name(), uid.to_num()), fg=fg.green))
            self.rfid.rfid.picc_halt_a()
        else:
            self.perror('Error reading card: {}'.format(result))


def setupLogger(name, log_level):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s %(levelname)8s [%(name)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def main():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-b', '--bus', type=int, help='The SPI bus (default = 0)', default=0)
    arg_parser.add_argument('-d', '--device', type=int, help='The SPI device (default = 0)', default=0)
    arg_parser.add_argument('-s', '--speed', type=int,
                            help='The max speed in Hz for the SPI device (default = 1000000)', default=1000000)
    arg_parser.add_argument('-r', '--pin_reset', type=int, help='The GPIO reset pin number (default = 25)', default=25)
    arg_parser.add_argument('-c', '--pin_ce', type=int,
                            help='The GPIO chip select pin number (default = 0, not connected)', default=0)
    arg_parser.add_argument('-i', '--pin_irq', type=int, help='The GPIO IRQ pin number (default = 24)', default=24)
    arg_parser.add_argument('-m', '--pin_mode', type=int,
                            help='GPIO pin numbering mode (default = GPIO.BCM)', default=GPIO.BCM)
    arg_parser.add_argument('--log_level',
                            help='Log level (ERROR, WARNING, INFO, DEBUG)', default='INFO')
    arg_parser.add_argument('--log_spi', type=bool,
                            help='Enable or disable SPI logging (requires --log_level=DEBUG)', default=False)
    arg_parser.add_argument('command', nargs='?',
                            help='optional command to run, if no command given, enter an interactive shell')
    arg_parser.add_argument('command_args', nargs=argparse.REMAINDER,
                            help='optional arguments for command')
    args = arg_parser.parse_args()

    setupLogger('mfrc522.log', args.log_level)
    setupLogger('mfrc522.trace', args.log_level)
    if args.log_spi:
        setupLogger('mfrc522.spi', args.log_level)

    try:
        rfid = SimpleMFRC522(bus=args.bus, device=args.device, speed=args.speed, pin_reset=args.pin_reset,
                             pin_ce=args.pin_ce, pin_irq=args.pin_irq, pin_mode=args.pin_mode)
        rfid.init()

        cli = MFRC522_Cli(rfid)
        if args.command:
            # we have a command, run it and then exit
            cli.onecmd_plus_hooks('{} {}'.format(args.command, ' '.join(args.command_args)))
        else:
            # we have no command, drop into interactive mode
            cli.cmdloop()
    finally:
        rfid.cleanup()


if __name__ == '__main__':
    main()
