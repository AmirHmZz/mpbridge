import click
import colorama

from . import bridge

colorama.init()


@click.group()
def main():
    pass


@main.command()
@click.argument('port')
def start(port):
    """PORT can be full path or :

            a[n]  connect to serial port "/dev/ttyACM[n]"

            u[n]  connect to serial port "/dev/ttyUSB[n]"

            c[n]  connect to serial port "COM[n]"
    """

    bridge.start(port)
