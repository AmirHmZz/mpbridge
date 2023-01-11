# 📂 MPBridge ![Python Version](https://img.shields.io/badge/Python-3.7%20or%20later-blue?style=flat-square) ![PyPI Version](https://img.shields.io/pypi/v/mpbridge?label=PyPI%20Version&style=flat-square) ![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/AmirHmZz/mpbridge/python-publish.yml?label=Builds&style=flat-square) ![PyPI - Downloads](https://img.shields.io/pypi/dm/MPbridge?label=Downloads&style=flat-square)

CLI tool to synchronise and manage files on a [MicroPython](https://github.com/micropython/micropython)
running device.

## 📥 Installation

`mpbridge` must be installed with `sudo` or `administrator` level of permission in order to be accessible in terminal:

* **Windows :** Open `cmd.exe` as administrator and run `pip install -U mpbridge`
* **Linux / MacOS :** Run `sudo pip install -U mpbridge`

## 🪄 How to use

You can use `mpbridge` in several ways based on your needs:

#### ⚜️ Bridge Mode

* Run `mpbridge bridge <PORT>`
* This mode copies all files and folders from your `MicroPython` board into a temporary directory on your local device
  and listens for any filesystem events on local directory to apply them on your board. It keeps raw repl open, so you
  cannot use serial port in other applications simultaneously.

#### ⚜️ Sync Directory

* Run `mpbridge sync <PORT> <DIR_PARH>`
* This command syncs a specified local directory with a `MicroPython` board. The sync process will push
  all modified files and folders into board and also pull changes from board and exits.
* If a conflict occurs, `mpbridge` will choose the **local version** of file automatically and
  overwrites it on connected board.

#### ⚜️ Development Mode

* Run `mpbridge dev <PORT> <DIR_PARH>`
* This mode repeats a loop of tasks in specified directory on `MicroPython` device as below :
    * _Sync files_ → _Wait for changes (Develop your project)_ → _Sync files_ → _Start MicroPython REPL_
* This mode is useful when you keep switching between different tools to flash and run new codes repeatedly.
  You can specify your project directory as `DIR_PATH` and `mpbridge` will take care of changes when you are developing
  your project in your desired IDE. You can switch to `MicroPython REPL` anytime you wish to run the updated code on
  your board.
* Automatic reset before entering MicroPython REPL can be enabled with `--auto-reset` option which can be set to
  `soft` (soft reset) or `hard` (hard reset).

#### ⚜️ Delete all files

* Run `mpbridge clear <PORT>`
* This command deletes all files and directories from `MicroPython` board and exits.

**Note** : `<PORT>` can be the **full port path** or one of the **short forms** below :

* `c[n]` for `COM[n]` (`c3` is equal to `COM3`)
* `u[n]` for `/dev/ttyUSB[n]` (`u3` is equal to `/dev/ttyUSB3`)
* `a[n]` for `/dev/ttyACM[n]` (`a3` is equal to `/dev/ttyACM3`)

## 👀 Ignore files

You can inform `mpbridge` to ignore syncing specific files or directories. This is useful when you don't want to sync
some directories like `.git/` or `venv/` with your board. To use this feature create a file named `mpbridge.ignore` in
your project directory and specify list of files and directories:

```
.git/
venv/
tests/test_1.py
tests/test_2.py
```

* `mpbridge.ignore` syntax is not as same as `.gitignore` files.
* At this time `mpbridge.ignore` only supports specifying file and directory paths directly.
* You should add a **slash** at the end of directory names: `dir1/`

## ✅ Supported platforms

- Windows
- MacOS
- Linux
- FreeBSD/BSD

## 📦 Dependencies

- Python 3.7 or above.
- [mpremote](https://pypi.org/project/mpremote/) >= 0.4.0
- [watchdog](https://pypi.org/project/watchdog/) >= 2.2.0
- [click](https://pypi.org/project/click/) >= 7.0
- [colorama](https://pypi.org/project/colorama/) >= 4.0
