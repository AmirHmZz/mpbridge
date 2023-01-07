import click
import colorama

from . import bridge

colorama.init()


@click.group()
def main():
    pass


@main.command("bridge", short_help='Starts bridge mode')
@click.argument('port')
def bridge_mode(port):
    """Starts bridge mode on <PORT>

    <PORT> can be full path or :

            a[n]  connect to serial port "/dev/ttyACM[n]"

            u[n]  connect to serial port "/dev/ttyUSB[n]"

            c[n]  connect to serial port "COM[n]"
    """

    bridge.start_bridge_mode(port)
