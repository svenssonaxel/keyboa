sendkey(1) "keyboa <VERSION>"

# NAME

sendkey - send key events to applications

# SYNOPSIS

sendkey [-doph]

# DESCRIPTION

*sendkey* reads key events on stdin and injects them in the event queue so that they are sent to applications.
The expected format is described in *keyboa*(5).

# OPTIONS

*-d*
	Dry run: Do not inject events.
*-o*
	Print events on stdout, in the form they are interpreted.
*-p*
	Pretty-print on stdout (implies -o).
*-h*
	Print help and exit.

# AUTHOR

Axel Svensson <mail@axelsvensson.com>

# SEE ALSO

*listenkey*(1), *keyboa*(5)
