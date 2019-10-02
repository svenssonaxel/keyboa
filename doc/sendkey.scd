sendkey(1) "keyboa <VERSION>"

# NAME

sendkey - send user input events to applications

# SYNOPSIS

sendkey [-doph]

# DESCRIPTION

*sendkey* reads user input events on stdin and injects them in the event queue so that they are sent to applications.
The expected format is described in *keyboa*(5).
If none of *-wx* is given, the default is
- *-w* if Windows mode is supported
- *-x* otherwise

# OPTIONS

*-w*
	Windows mode: Inject events using Windows API.
*-x*
	X11 mode: Inject events into X11 session.
*-o*
	Print events on stdout, in the form they are interpreted.
*-p*
	Pretty-print on stdout (implies -o).
*-d*
	Dry run: Do not inject events.
*-h*
	Print help and exit.

# AUTHOR

Axel Svensson <mail@axelsvensson.com>

# SEE ALSO

*listenkey*(1), *keyboa*(5)
