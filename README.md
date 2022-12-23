# 📂 MPBridge
A file system bridge to synchronise and manage files on a [MicroPython](https://github.com/micropython/micropython) running device

## How it works
This tool doesn't provide any graphical user interface and uses platform's file system instead to make it easier to manage files on remote device. After starting the bridge, all files will be copied from MicroPython device into a temporary directory in your local mechine and all modifications will be applied to remote device too, so you would be able to use any tool or file manager to manage or modify files.

## Supported platforms
- Windows
- MacOS
- Linux
- FreeBSD/BSD

## Dependencies
- Python 3.7 or above.
- [mpremote](https://pypi.org/project/mpremote/) >= 0.4.0
- [watchdog](https://pypi.org/project/watchdog/) >= 2.2.0
- [click](https://pypi.org/project/click/) >= 7.0
- [colorama](https://pypi.org/project/colorama/) >= 4.0

## Installation
`mpbridge` must be installed with `sudo` or `administrator` level of permission in order to be accessible in terminal:
### Windows
* Open `cmd.exe` as administrator and run `pip install -U mpbridge`
### Linux / MacOS
* Run `sudo pip install -U mpbridge`

## How to use
1. Connect your MicroPython device
2. Run `mpbridge start <PORT>`
