Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
License: See LICENSE

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

## Building from source

Currently, building is only tested on Cygwin.

Dependencies:
- mingw32 compiler (cygwin package mingw64-i686-gcc-core)
- scdoc (https://git.sr.ht/~sircmpwn/scdoc)

Run `make`. Done.

## Running

To use the release, you will probably want to have Python 3 installed but it is not required.

listenkey.exe and sendkey.exe are standalone applications. Run `listenkey -h` and `sendkey -h` for help.

See `layout1.py` and `layout2.py` for examples of how to write and run a processor.

## Warnings

### Use with care

listenkey.exe with the -c option will prevent key events from reaching the applications. Unless you use it in combination with the -e or -d option, you run the risk of partly losing control of your computer. This particular foot gun is necessary for the core functionality, so it will stay this way. The recommended and conservative use is to always have the -e option turned on. This way, if your processor hits a snag you can always press Esc to exit listenkey.exe. In order to make use of this option, you will need a layout that doesn't require using the Esc key.

### Known bugs

For security reasons, Windows does not allow all key event to be scoped up by an application like keyboa is attempting to do. Sometimes, a key down event can be sent to keyboa while the key up event is withheld. This can for example happen when Win+L is pressed to lock the desktop, or when switching to an application running with elevated privileges. From the perspective of your processor, this will look like a key being held down indefinitely. There is library functionality that attempts to compensate for this situation (unstick_keys), but it is not perfect.

### Alpha stage code

This code is in alpha stage, and the API will not be stable before release of version 2.0.0.
