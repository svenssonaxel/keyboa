#!/usr/bin/env python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# Legal: See COPYING.txt

# This is a minimal example of how to use libkeyboa. It switches Left Control
# and Caps Lock.
#
# Run in cmd:
#   listenkey -ces | python3 layout2.py | sendkey
#
# Or in cygwin:
#   ./listenkey -ces | ./layout2.py | ./sendkey

from libkeyboa import *

mapping={
	"VK_CAPITAL": "VK_LCONTROL",
	"VK_LCONTROL": "VK_CAPITAL",
	}

@retgen
def remap(gen):
	for obj in gen:
		if(obj["type"] in ["keydown", "keyup", "keypress"]):
			vks=obj["win_virtualkey_symbol"]
			if(vks in mapping):
				yield {"type": obj["type"], **data.vkeyinfo(mapping[vks])}
				continue
		yield obj

list_of_transformations = [
	tr.keyboa_input(),                                      # libkeyboa
	tr.altgr_workaround_input(),                            # libkeyboa
	tr.enrich_input(),                                      # libkeyboa
	remap(),                                                # layout2
	tr.altgr_workaround_output(),                           # libkeyboa
	tr.keyboa_output()]                                     # libkeyboa

keyboa_run(list_of_transformations)
