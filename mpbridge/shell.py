import click
import colorama

from . import bridge

colorama.init()


@click.group()
def main():
    pass


@main.command("bridge", short_help='Start bridge mode')
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
@click.option('--clean', "-c", is_flag=True, help="Perform a clean sync")
def sync(port, dir_path, clean):
    """Sync files of <PORT> with specified directory <DIR_PATH>

    <PORT> can be full path or :

            a[n]  connect to serial port "/dev/ttyACM[n]"

            u[n]  connect to serial port "/dev/ttyUSB[n]"

            c[n]  connect to serial port "COM[n]"
    """
    bridge.sync(port, dir_path, clean)


@main.command("dev", short_help='Start development mode')
@click.argument('port')
@click.argument('dir_path', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.option('--auto-reset', help="Enables auto reset before entering REPL",
              type=click.Choice(['soft', 'hard'], case_sensitive=False))
@click.option('--no-prompt', is_flag=True, help="Disables prompt for entering REPL")
def dev(port, dir_path, auto_reset, no_prompt: bool):
    """Start development mode on <PORT> in specified directory <DIR_PATH>

    <PORT> can be full path or :

            a[n]  connect to serial port "/dev/ttyACM[n]"

            u[n]  connect to serial port "/dev/ttyUSB[n]"

            c[n]  connect to serial port "COM[n]"
    """
    bridge.start_dev_mode(port, dir_path, auto_reset=auto_reset, no_prompt=no_prompt)


@main.command("clear", short_help='Delete all files from MicroPython device')
@click.argument('port')
def clear(port):
    """Delete all files from MicroPython device connected to <PORT>

    <PORT> can be full path or :

            a[n]  connect to serial port "/dev/ttyACM[n]"

            u[n]  connect to serial port "/dev/ttyUSB[n]"

            c[n]  connect to serial port "COM[n]"
    """
    bridge.clear(port=port)


@main.command("list", short_help='List available devices')
def list_devices():
    """List available devices

    [device] [serial_number] [vid]:[pid] [manufacturer] [product]
        """
    bridge.list_devices()
