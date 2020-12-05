import argparse
import cmd2
import RPi.GPIO as GPIO
from .simple_mfrc522 import SimpleMFRC522
from cmd2 import style, fg


class MFRC522_Cli(cmd2.Cmd):

    def __init__(self, rfid):
        super().__init__(allow_cli_args=False)

        self.intro = style('''

█▀▄▀█ █▀▀ █▀▀█ █▀▀ █▀▀ █▀█ █▀█
█░▀░█ █▀▀ █▄▄▀ █░░ ▀▀▄ ░▄▀ ░▄▀
▀░░░▀ ▀░░ ▀░▀▀ ▀▀▀ ▄▄▀ █▄▄ █▄▄

''', fg=fg.blue)

        self.prompt = style('➜ ', fg=fg.green, bold=True)
        self.rfid = rfid

    def do_version(self, args):
        firmware = self.rfid.firmware_version()
        self.poutput('Firmware Version: {:#x} = {} - {}'.format(firmware.value, firmware.version, firmware.description))

    def do_selftest(self, args):
        firmware = self.rfid.firmware_version()
        self.poutput('Firmware Version: {:#x} = {} - {}'.format(firmware.value, firmware.version, firmware.description))

        result = self.rfid.selftest()
        self.poutput('Selftest Result: {}'.format('OK' if result else 'DEFECT or UNKNOWN'))

    def do_read(self, args):
        pass

    def do_write(self, args):
        pass


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
    arg_parser.add_argument('command', nargs='?',
                            help='optional command to run, if no command given, enter an interactive shell')
    arg_parser.add_argument('command_args', nargs=argparse.REMAINDER,
                            help='optional arguments for command')
    args = arg_parser.parse_args()

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
