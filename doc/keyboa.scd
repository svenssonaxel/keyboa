keyboa(5) "keyboa <VERSION>"

This is a description of the format used by *listenkey* and *sendkey*.

The keyboa tools attempt to do one thing only and do it well, namely

- *listenkey*: access incoming key events, optionally consuming them
- *libkeyboa*: manipulate key events
- *sendkey*: send key events to applications

While libkeyboa has some functionality for manipulating key events in a platform independent manner,
*listenkey* and *sendkey* make no attempt to hide or bridge platform specific concerns.
For this reason the format is necessarily somewhat platform dependent.

The format that *listenkey* uses for printing messages on stdout,
and that *sendkey* uses for consuming messages on stdin,
is a stream of messages where each message is a JSON object.
*listenkey* prints one message per line, but *sendkey* has no requirements for newline placement.

Below is a description of each message type and field.
*sendkey* will ignore any field not specified here,
and any message of a type not specified here.
The intention is to allow the user to arbitrarily add message types as well as add fields to the existing types.
Many functions in *libkeyboa* do.

# Message types

The meaning of a message depends on the message type.
The message type is specified in the "type" field of the message.

## buttondown
- Represents: The pressing down of a mouse button
- Produced by listenkey: on all platforms
- Handled by sendkey: on all platforms

## buttonup
- Represents: The release of a mouse button
- Produced by listenkey: on all platforms
- Handled by sendkey: on all platforms

## init
- Represents: No event
- Produced by listenkey: At startup, if the *-l* option is provided
- Handled by sendkey: never

Contains information about the current keyboard layout and state.

## keydown
- Represents: The pressing down of a key
- Produced by listenkey: on all platforms
- Handled by sendkey: on all platforms

## keypress
- Represents: The pressing down of a key followed by the release of the same key
- Produced by listenkey: never
- Handled by sendkey: on all platforms

## keyup
- Represents: The release of a key
- Produced by listenkey: on all platforms
- Handled by sendkey: on all platforms

## pointermove
- Represents: The movement of a mouse or another pointing device
- Produced by listenkey: on all platforms
- Handled by sendkey: on all platforms

## wheel
- Represents: The rotation of a mouse wheel or corresponding action from another pointing device
- Produced by listenkey: on all platforms
- Handled by sendkey: on all platforms

# Fields

## unicode_codepoint

- Present in message types: keydown, keyup, keypress
- Produced by listenkey: never
- Handled by sendkey: on all platforms
- Values: integer, valid unicode codepoint

If unicode_codepoint is present, sendkey will use it to construct the key events to send to the operating system.
If unicode_codepoint is not present, sendkey requires a native key designator to be present, and uses that instead.

On windows, a native key designator is one or both of:
- win_scancode
- win_virtualkey

If present, it means that the key event is to be handled with a mechanism that allows any unicode character to be sent to an application.
This differs from a native designator in several ways:
- On windows, a virtualkey can represent different characters depending on the shift state, e.g. "T" and "t", or "5" and "%".
When using unicode_codepoint, the 

## win_button

- Present in message types: buttondown, buttonup
- Produced by listenkey: on windows only
- Handled by sendkey: not implemented yet
- Values: L, R, M, X1 or X2

The name of the mouse button.
L, R and M means left, right and middle, respectively.

## win_altdown
- Present in message types: keydown, keyup, keypress
- Produced by listenkey: on windows only
- Handled by sendkey: never
- Values: true/false

The LLKHF_ALTDOWN flag.

Note that the Alt key produces keydown and keyup events just like any other key.
This field is somewhat redundant, but is provided for completeness.

Reference: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct

## win_eventname

- Present in message types: keydown, keyup, pointermove, wheel, buttondown, buttonup
- Produced by listenkey: on windows only
- Handled by sendkey: never
- Values: A string matching /WM_((SYS)?KEY(DOWN|UP)|MOUSE(MOVE|WHEEL)|(NC)?[LRMX]BUTTON(DOWN|UP|DBLCLK)|MENURBUTTONUP)/

The name of the Windows API message.

## win_extended
- Present in message types: keydown, keyup, keypress
- Produced by listenkey: on windows only
- Handled by sendkey: on windows only
- Values: true/false

The LLKHF_EXTENDED flag.
If true, the scan code was preceded by a prefix byte that has the value 0xE0.

Reference:
- https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct
- https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-keybdinput

## win_injected
- Present in message types: keydown, keyup, keypress
- Produced by listenkey: on windows only
- Handled by sendkey: ignored
- Values: true/false

The LLKHF_INJECTED flag.
If true, then the event was injected.
This could for example mean that the event comes from *sendkey* rather than the keyboard.

Reference: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct

By default, listenkey will not print injected key events.
This is because sendkey works by way of injecting key events.
If you use the `-i` flag to make listenkey print injected events also and pipe these to sendkey, you risk creating an infinite loop.

## win_lower_il_injected
- Present in message types: keydown, keyup, keypress
- Produced by listenkey: on windows only
- Handled by sendkey: ignored
- Values: true/false

The LLKHF_LOWER_IL_INJECTED flag.
If win_injected and win_lower_il_injected are both true, then the event was injected from a process running at lower integrity level.

Reference: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct

## win_pointerx, win_pointery

- Present in message types: pointermove, wheel, buttondown, buttonup
- Produced by listenkey: on windows only
- Handled by sendkey: not implemented yet
- Values: integer

The x and y coordinate, respectively, for the new pointer position.

These seem to be values calculated by adding the mouse move delta to the current pointer position.
This has a few implications:
- The reported position may well be outside of the screen.
- Attempting to calculated the delta by subtracting the previously reported position might yield incorrect results if the events are consumed.

## win_scancode
- Present in message types: keydown, keyup, keypress
- Produced by listenkey: on windows only
- Handled by sendkey: on windows only
- Value: a valid scancode as an integer

The hardware scan code for the key, as it is provided by the Windows API.
This means that the prefix 0xE0 is provided as a flag (see win_extended) and that the prefix 0xE1 isn't provided at all.

Reference:

- https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-keybdinput
- https://download.microsoft.com/download/1/6/1/161ba512-40e2-4cc9-843a-923143f3456c/scancode.doc

## win_time

- Present in message types: keydown, keyup, keypress
- Produced by listenkey: on windows only
- Handled by sendkey: on windows only
- Values: integer [0 - 4294967295]

The elapsed time, in milliseconds, from the time the system was started to the time the key event was created.
Will wrap around at 2^32 (more than 49 days).

Reference:
- https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct
- https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getmessagetime

## win_virtualkey
- Present in message types: keydown, keyup, keypress
- Produced by listenkey: on windows only
- Handled by sendkey: on windows only
- Value: a valid virtualkey as an integer

The Windows virtual key code.

Reference: https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes

## win_wheeldeltax, win_wheeldeltay

- Present in message types: wheel
- Produced by listenkey: on windows only, when the event regards the horizontal or vertical mouse wheel, respectively
- Handled by sendkey: not implemented yet
- Values: integer

A positive value means the horizontal wheel was rotated to the right, negative to the left.
On wheel click is 120.

Reference: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-msllhookstruct

# AUTHOR

Axel Svensson <mail@axelsvensson.com>

# VERSION

This manual page is part of keyboa version <VERSION>.

# SEE ALSO

*listenkey*(1), sendkey*(1)
