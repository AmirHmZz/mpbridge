# 📂 MicroPython File Manager
A new tool for managing files on a MicroPython running device based on [mpremote](https://pypi.org/project/mpremote)

## How it works
This tool doesn't propose any graphical user interface and uses platform's file explorer to make it easier to manage files on remote device.
It uses [mpremote](https://pypi.org/project/mpremote) as a standard comminunication utility to manage files on MicroPython devices.

## Supported platforms
- Windows
- MacOS
- Linux
- FreeBSD/BSD

## Dependencies
- Python 3.7 or above.
- [Watchdog](https://pypi.org/project/watchdog/) 2.2.0 or above.
- [Click](https://pypi.org/project/click/) 8.0 or above.

## How to use
1. Install [mpremote](https://pypi.org/project/mpremote) on local machine.
2. Add `mpremote` executable to `PATH` if it's not accessible from shell.
3. Clone repository and Install dependencies in `requirements.txt`.
4. Connect your MicroPython running device and do `python main.py <PORT>`.
