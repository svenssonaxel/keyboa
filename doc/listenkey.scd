listenkey(1) "keyboa <VERSION>"

# NAME

listenkey - access incoming key events, optionally consuming them

# SYNOPSIS

listenkey [-cCiedlLfh]

# DESCRIPTION

*listenkey* provides access to incoming key events, optionally withholding them from applications.
This will for example allow a user to process key events arbitrarily and send them along to applications using *sendkey*(1).
The output format is described in *keyboa*(5).

# OPTIONS

*-k*
	Print keyboard events. This option is on by default unless -m or -b is provided.

*-m*
	Print mouse move events.

*-b*
	Print mouse button and wheel events.

*-c*
	Consume non-injected events, of all types specified with *-k*, *-m* and *-b*.
	This prevents the specified events from reaching applications.

*-C*
	Consume injected events, of all types specified with *-k*, *-m* and *-b*.
	This prevents the specified events from reaching applications.

*-i*
	Also print injected events, of all types specified with *-k*, *-m* and *-b*.
	Without this flag, only non-injected events are printed.

*-e*
	Exit when escape key is pressed.

*-d*
	Exit after 20 events are processed (useful for debugging).

*-l*
	At startup, print a message containing information about the current keyboard layout and state.

*-L*
	Exit after printing startup message (implies -l).

*-h*
	Print help and exit.

# WARNING

When *listenkey* is called with the *-c* option, it will prevent key events from reaching the applications.
Unless you use it in combination with the *-e* or *-d* option, you run the risk of partially losing control of your computer.
This particular foot gun is necessary for the core functionality, so it will stay this way.
For every-day use, the recommended and conservative choice is to use *-c* in combination with *-e*.
This way you can at least exit *listenkey* by pressing Esc.
This will unfortunately prevent you from using Esc normally.

# AUTHOR

Axel Svensson <mail@axelsvensson.com>

# VERSION

This manual page is part of keyboa version <VERSION>.

# SEE ALSO

*sendkey*(1), *keyboa*(5)