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


@main.command("sync", short_help='Sync files with a directory')
@click.argument('port')
@click.argument('dir_path', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
def sync(port, dir_path):
    """Sync files of <PORT> with specified directory <DIR_PATH>

    <PORT> can be full path or :

            a[n]  connect to serial port "/dev/ttyACM[n]"

            u[n]  connect to serial port "/dev/ttyUSB[n]"

            c[n]  connect to serial port "COM[n]"
    """
    bridge.sync(port, dir_path)
