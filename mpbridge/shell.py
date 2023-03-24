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
    """Starts bridge mode on [PORT]

    [PORT] can be full path or :

            a[n]  connect to serial port "/dev/ttyACM[n]"

            u[n]  connect to serial port "/dev/ttyUSB[n]"

            c[n]  connect to serial port "COM[n]"
    """

    bridge.start_bridge_mode(port)


@main.command("sync", short_help='Sync files with a directory')
@click.argument('port')
@click.argument('dir_path', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True), default="")
@click.option('--clean', "-c", is_flag=True,
              help="Execute Clean Sync")
@click.option('--push-only', "-p", is_flag=True,
              help="Only push changes without pulling anything from remote device")
@click.option('--dry-run', "-d", is_flag=True,
              help="Test Sync command without performing any actions")
def sync(port, dir_path, clean, dry_run, push_only):
    """Sync files of on [PORT] in specified directory [DIR_PATH]

    If [DIR_PATH] is not set, it defaults to the current path

    [PORT] can be full path or :

            a[n]  connect to serial port "/dev/ttyACM[n]"

            u[n]  connect to serial port "/dev/ttyUSB[n]"

            c[n]  connect to serial port "COM[n]"

    Sync files:

            Pull the files that are not in the local but exist in the device to the local.

            Push files that are not in the device but exist locally to the device.

            Check the hash of the files both in the local and the device,

            and then push the different files from the local to the device.

    Clean Sync files:

            Delete files from the device that do not exist locally but exist on the device.

            Push files that are not in the device but exist locally to the device.

            Check the hash of the files both in the local and the device,

            and then push the different files from the local to the device.
    """
    bridge.sync(port, dir_path, clean, dry_run, push_only)


@main.command("dev", short_help='Start development mode')
@click.argument('port')
@click.argument('dir_path', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True), default="")
@click.option('--auto-reset', help="Enables auto reset before entering REPL",
              type=click.Choice(['soft', 'hard'], case_sensitive=False))
@click.option('--no-prompt', is_flag=True, help="Disables prompt, auto Clean Sync & enter REPL")
def dev(port, dir_path, auto_reset, no_prompt: bool):
    """Start development mode on [PORT] in specified directory [DIR_PATH]

    If [DIR_PATH] is not set, it defaults to the current path

    [PORT] can be full path or :

            a[n]  connect to serial port "/dev/ttyACM[n]"

            u[n]  connect to serial port "/dev/ttyUSB[n]"

            c[n]  connect to serial port "COM[n]"

    Workflow:

            Sync files → if keyboard `Enter` → Clean Sync files → REPL → if keyboard `ctrl+]` → back loop

            if --no-prompt → Clean Sync files → REPL → if keyboard `ctrl+]` → back loop

            When not in the REPL, keyboard `ctrl+C` exits the workflow

    Sync files:

            Pull the files that are not in the local but exist in the device to the local.

            Push files that are not in the device but exist locally to the device.

            Check the hash of the files both in the local and the device,

            and then push the different files from the local to the device.

    Clean Sync files:

            Delete files from the device that do not exist locally but exist on the device.

            Push files that are not in the device but exist locally to the device.

            Check the hash of the files both in the local and the device,

            and then push the different files from the local to the device.
    """
    bridge.start_dev_mode(port, dir_path, auto_reset=auto_reset, no_prompt=no_prompt)


@main.command("clear", short_help='Delete all files from MicroPython device')
@click.argument('port')
def clear(port):
    """Delete all files from MicroPython device connected to [PORT]

    [PORT] can be full path or :

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
