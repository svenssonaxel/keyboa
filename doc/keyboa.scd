
# INTRODUCTION

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

# MESSAGE TYPES

The meaning of a message depends on the message type.
The message type is specified in the "type" field of the message.

## buttondown
- Represents: The pressing down of a mouse button
- Produced by listenkey: all modes
- Handled by sendkey: all modes

## buttonup
- Represents: The release of a mouse button
- Produced by listenkey: all modes
- Handled by sendkey: all modes

## init
- Represents: No event
- Produced by listenkey: At startup, if the *-s* option is provided
- Handled by sendkey: ignored

Contains information about the current keyboard layout and state.

## keydown
- Represents: The pressing down of a key
- Produced by listenkey: all modes
- Handled by sendkey: all modes

## keypress
- Represents: The pressing down of a key followed by the release of the same key
- Produced by listenkey: never
- Handled by sendkey: all modes

## keyup
- Represents: The release of a key
- Produced by listenkey: all modes
- Handled by sendkey: all modes

## pointermove
- Represents: The movement of a mouse or another pointing device
- Produced by listenkey: all modes
- Handled by sendkey: all modes

## wheel
- Represents: The rotation of a mouse wheel or corresponding action from another pointing device
- Produced by listenkey: all modes
- Handled by sendkey: all modes

# FIELDS

## type
- Present in message types: all
- Produced by listenkey: always
- Handled by sendkey: always
- Value: string

The message type.
This affects the meaning of the message and what fields are possible or mandatory.

## unicode_codepoint
- Present in message types: keydown, keyup and keypress
- Produced by listenkey: never
- Handled by sendkey: all modes, optional
- Value: integer, valid unicode codepoint

If unicode_codepoint is present, sendkey will use it to construct the key events to send to the operating system.
If unicode_codepoint is not present, a native key designator is mandatory.

On windows, a native key designator is one or both of:

- win_scancode
- win_virtualkey

If present, it means that the key event is to be handled with a mechanism that allows any unicode character to be sent to an application.
This differs from a native designator in several ways:

- On windows, a virtualkey can represent different characters depending on the shift state, e.g. "T" and "t", or "5" and "%", while a keyevent with a unicode codepoint depends on no such context.
- On windows, if a unicode codepoint requires two utf-16 code units, it will be sent as who separate key events.

## win_altdown
- Present in message types: keydown, keyup, keypress
- Produced by listenkey: Windows mode only
- Handled by sendkey: ignored
- Value: true/false

The LLKHF_ALTDOWN flag.

Note that the Alt key produces keydown and keyup events just like any other key.
This field is somewhat redundant, but is provided for completeness.

Reference: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct

## win_button
- Present in message types: buttondown and buttonup
- Produced by listenkey: Windows mode only
- Handled by sendkey: Windows mode only, required
- Value: string

The name of the mouse button.

The value will typically be one of the following values:

- "L" for the left mouse button
- "R" for the right mouse button
- "M" for the middle mouse button
- "X1"
- "X2"

sendkey is guaranteed to handle the values listed above, but listenkey may emit others.

## win_eventname
- Present in message types: keydown, keyup, pointermove, wheel, buttondown, buttonup
- Produced by listenkey: Windows mode only
- Handled by sendkey: ignored
- Value: string

The name of the Windows API message.

The value will typically be, but is not guaranteed to be, one of the following:

- "WM_LBUTTONDOWN"
- "WM_LBUTTONUP"
- "WM_MBUTTONDOWN"
- "WM_MBUTTONUP"
- "WM_MOUSEHWHEEL"
- "WM_MOUSEMOVE"
- "WM_MOUSEWHEEL"
- "WM_RBUTTONDOWN"
- "WM_RBUTTONUP"
- "WM_XBUTTONDOWN"
- "WM_XBUTTONUP"

## win_extended
- Present in message types: keydown, keyup, keypress
- Produced by listenkey: Windows mode only
- Handled by sendkey: Windows mode only, optional
- Values: true/false

The LLKHF_EXTENDED flag.
If true, the scan code is preceded by a prefix byte that has the value 0xE0.

Reference:

- https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct
- https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-keybdinput

## win_injected
- Present in message types: keydown, keyup, keypress
- Produced by listenkey: Windows mode only
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
- Produced by listenkey: Windows mode only
- Handled by sendkey: ignored
- Values: true/false

The LLKHF_LOWER_IL_INJECTED flag.
If win_injected and win_lower_il_injected are both true, then the event was injected from a process running at lower integrity level.

Reference: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct

## win_pointerx_..., win_pointery_...
- Present in message types: pointermove
- Produced by listenkey: Windows mode only, primpixel coordinate system only
- Handled by sendkey: Windows mode only, at least one of coordinate systems "rellegacyacc", "primprim" or "virtvirt", required
- Values: integer

win_pointerx_[CS] and win_pointery_[CS] are the x and y coordinates, respectively, for the new pointer position, in coordinate system [CS]. The Windows API has at least four separate coordinate systems, each having a pair of fields:

- win_pointerx_primpixel, win_pointery_primpixel
- win_pointerx_primprim, win_pointery_primprim
- win_pointerx_rellegacyacc, win_pointery_rellegacyacc
- win_pointerx_virtvirt, win_pointery_virtvirt

The coordinate system is [origin][scale][acc] where

- [origin] determines the placement of the origin, coordinate (0,0):
  - "Rel": The origin is at the current pointer position.
  - "Prim": The origin is at the top-left corner of the primary monitor.
  - "Virt": The origin is at the top-left corner of the virtual desktop (the smallest rectangle enclosing all monitors).
- [scale] determines the unit:
  - "Pixel": The unit is 1 pixel.
  - "Legacy": The unit is one pixel scaled as for a non DPI aware application, catering to the legacy assumption of 96 DPI.
  - "Prim": The system is normalized so that both the width and height of the primary monitor is 65536.
  - "Virt": The system is normalized so that both the width and height of the virtual desktop (the smallest rectangle enclosing all monitors) is 65536.
- [acc] is "Acc" if the motion is subject to acceleration, otherwise nothing.

Currently, listenkey can only report using the coordinate system "primpixel", while sendkey can only accept "rellegacyacc", "primprim" and "virtvirt".

For listenkey, the coordinates seem to be values calculated by adding the mouse move delta to the current pointer position.

This has a few implications:

- The reported coordinates may well be outside of the screen.
- Attempting to calculate the delta by subtracting the previously reported position might yield incorrect results if the events are consumed.

If one coordinate is present but not the other, sendkey will assume the other coordinate is zero.
If coordinates from more than one system are present, sendkey will attempt to use, in order: "rellegacyacc", "primprim" and "virtvirt".

Reference: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput

## win_scancode
- Present in message types: keydown, keyup, keypress
- Produced by listenkey: Windows mode only
- Handled by sendkey: Windows mode only, required if win_virtualkey and unicode_codepoint are both absent
- Value: a valid scancode as an integer

The hardware scan code for the key, as it is provided by the Windows API.
This means that the prefix 0xE0 is provided as a flag (see win_extended) and that the prefix 0xE1 isn't provided at all.

Reference:

- https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-keybdinput
- https://download.microsoft.com/download/1/6/1/161ba512-40e2-4cc9-843a-923143f3456c/scancode.doc

## win_time

- Present in message types: keydown, keyup, keypress
- Produced by listenkey: Windows mode only
- Handled by sendkey: Windows mode only
- Values: integer [0 - 4294967295]

The elapsed time, in milliseconds, from the time the system was started to the time the key event was created.
Will wrap around at 2^32 (more than 49 days).

Reference:

- https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct
- https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getmessagetime

## win_virtualkey
- Present in message types: keydown, keyup, keypress
- Produced by listenkey: Windows mode only
- Handled by sendkey: Windows mode only, required if win_scancode and unicode_codepoint are both absent
- Value: a valid virtualkey as an integer

The Windows virtual key code.

Reference: https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes

## win_wheeldeltax, win_wheeldeltay

- Present in message types: wheel
- Produced by listenkey: Windows mode only, exactly one of win_wheeldeltax and win_wheeldeltay present
- Handled by sendkey: Windows mode only, exactly one of win_wheeldeltax and win_wheeldeltay required
- Values: integer, for sendkey in the range (-12000, 12000)

For win_wheeldeltax, a positive value means the horizontal wheel was rotated to the right, and a negative value means to the left.

For win_wheeldeltay, a positive value means the vertical wheel was rotated forward, away from the user, and a negative value means backward, toward the user.

One wheel click is 120.

The range limit is imposed by sendkey only, not by Windows.
There is no range guarantee for listenkey.

Reference: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-msllhookstruct

# AUTHOR

Axel Svensson <mail@axelsvensson.com>

# VERSION

This manual page is part of keyboa version <VERSION>.

# SEE ALSO

*listenkey*(1), *sendkey*(1)
