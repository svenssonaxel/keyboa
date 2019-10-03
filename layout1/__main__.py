# Requires python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# Legal: See COPYING.txt

# This is a rather involved example, including
# - Any key functioning as both modifier and letter (events_to_chords)
# - Layout planes/layers, selectable using any number of modifiers (load, w, ch)
# - Chords transformed to other operations (chords_to_scripts)
# - Notation for key combinations, series, and repetition (scripts_to_chords)
# - Key renaming and aliasing (using commonnamesdict)
# - Chords manipulating state (boxdrawing, unicode_input, compose)
# - Repetition of chords based on a numeric argument (numarg_multiplier)
# - Output depending on time (printdate)
# - Input characters by unicode codepoint (unicode_input)
# - Dead chords for composing characters
#
# Run in cmd:
#   listenkey -cel | python3 -m layout1 | sendkey
#
# Or in cygwin:
#   ./listenkey -cel | python3 -m layout1 | ./sendkey

import layout1.config as c
import layout1.tr as l1
from libkeyboa import *
import argparse, sys

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--state", required=False, help="The file used to persist state. Default: No persistence.")
ap.add_argument("-i", "--in",    required=False, help="The file used to input key events. Default: stdin.")
ap.add_argument("-o", "--out",   required=False, help="The file used to output key events. Default: stdout.")
ap.add_argument("-e", "--err",   required=False, help="The file used to output errors. Default: stderr.")
ap.add_argument("-u", "--ui",    required=False, help="The terminal used for UI. Default: stderr.")
args = vars(ap.parse_args())
statefilename=args['state']
infile=sys.stdin
outfile=sys.stdout
uifile=sys.stderr
if(args["in"]): infile=open(args["in"], "r")
if(args["out"]): outfile=open(args["out"], "w")
if(args["err"]): sys.stderr=open(args['err'], "w")
if(args["ui"]): uifile=open(args["ui"], "w")

list_of_transformations = [
	tr.input_events(file=infile),                           # libkeyboa
	tr.releaseall_at_init(),                                # libkeyboa
 	l1.exit_on_escape(),                                    # layout1
	tr.altgr_workaround_input(),                            # libkeyboa
	tr.loadstate(statefilename),                            # libkeyboa
	tr.add_commonname(),                                    # libkeyboa
	tr.allow_repeat("physkey"),                             # libkeyboa
	tr.unstick_keys("commonname", c.key_timeouts),          # libkeyboa
	tr.events_to_chords("commonname"),                      # libkeyboa
	l1.enrich_chord("mods", "modes"),                       # layout1
	l1.modlock({"Modlock"}, "Modlock", "space"),            # layout1
	l1.modeswitch({"Modlock","Ctrl"}, "Modeswitch"),        # layout1
	l1.macro_and_multiplier_controller(),                   # layout1
	l1.numarg_multiplier(),                                 # layout1
	tr.macro(l1.macrotest, "macros"),                       # libkeyboa
	l1.chords_to_scripts(),                                 # layout1
	l1.compose("compose:"),                                 # layout1
	l1.scripts_to_chords(),                                 # layout1
	l1.boxdrawings("b"),                                    # layout1
	l1.unicode_input(),                                     # layout1
	l1.printdate("Printdate"),                              # layout1
	l1.wait("Wait"),                                        # layout1
	tr.chords_to_events("commonname"),                      # libkeyboa
	tr.ratelimit(40, l1.ratelimit_filter_updown),           # libkeyboa
	tr.ratelimit(1000, l1.ratelimit_filter_keyevent),       # libkeyboa
	tr.resolve_commonname(),                                # libkeyboa
	l1.resolve_characters(),                                # layout1
	tr.altgr_workaround_output(),                           # libkeyboa
	l1.termui(file=uifile),                                 # layout1
	tr.savestate(statefilename),                            # libkeyboa
	tr.output_events(file=outfile)]                         # libkeyboa

keyboa_run(list_of_transformations)
