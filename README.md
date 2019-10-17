Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
Legal: See COPYING.txt

# Keyboa

Keyboa is a flexible tool for customizing keyboard functionality. It is intended for power users with some scripting skill, or as a starting point for developing a keyboard customization application.

It gives the user complete programmatic control over the key-event stream (to the limits imposed by the OS). That way, it goes far beyond mere layout customization.

## Design

The system is designed as a stream processing pipeline, and has three major parts.

The first part in the pipeline is the listener. It plugs into the event stream coming from the keyboard, reads the key events, prevents them from being handled by applications, converts them to a simple format and prints them on stdout. On Windows, this is listenkey.exe.

The second part is the processor, and is defined by the user. It can be any program that reads key events from stdin in a simple format, processes them in any suitable way, and prints the resulting key events on stdout. You can write your processor in any language you please, but if you choose to use Python you will have the advantage of libkeyboa, a Python library custom made for this purpose.

The third part reads key events on stdin and sends them along to applications as if they came from the keyboard. On Windows, this is sendkey.exe.

## Systems supported

Currently, only Windows is supported. The ambition is to support Linux soon. MacOS could be considered at a later time.

## Downloading

You can download a release at https://github.com/svenssonaxel/keyboa/releases

## Building from source

Building is tested on Cygwin and Debian.
The make scripts will attempt to detect missing dependencies and give hints on how to install them.

Dependencies:
- mingw32 for building Windows executables
- gcc for building Linux executables
- scdoc for building man pages
- pandoc for building html and pdf documentation

Run `make`. Done.
You can then install with `make install` and uninstall with `make uninstall`.

## Running

A release contains:

- Pre-built, standalone executables `listenkey.exe` and `sendkey.exe`
- Ready-to-use Python 3 library `libkeyboa`
- Documentation in man, HTML and PDF formats

For quick reference, run `listenkey -h` and `sendkey -h`.

See `layout1/__main__.py` and `layout2.py` for examples of how to write and run a processor using `libkeyboa`.

## Warnings

### Use with care

`listenkey` with the `-c` option will prevent key events from reaching the applications. Unless you use it in combination with the `-e` or `-d` option, you run the risk of partially losing control of your computer. This particular foot gun is necessary for the core functionality, so it will stay this way. For every-day use, the recommended and conservative choice is to use `-c` in combination with `-e`. This way you can at least exit `listenkey` by pressing Esc.

### Alpha stage code

Keyboa is in alpha stage. The `keyboa-API` format and the CLI interface to `listenkey` and `sendkey` will not be stable until the release of keyboa version 2.0.0.
