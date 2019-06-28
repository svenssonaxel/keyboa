#!/usr/bin/env python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# License: See LICENSE

# This is a minimal example of how to use libkeyboa. It switches Left Control
# and Caps Lock.
#
# Run in cmd:
#   listenkey -cel | python3 layout2.py | sendkey
#
# Or in cygwin:
#   ./listenkey -cel | ./layout2.py | ./sendkey

from libkeyboa import *

mapping={
	"VK_CAPITAL": "VK_LCONTROL",
	"VK_LCONTROL": "VK_CAPITAL"}

@retgen
def remap(gen):
	for obj in gen:
		if(obj["type"] in ["keydown", "keyup", "keypress"]):
			vks=obj["win_virtualkey_symbol"]
			if(vks in mapping):
				yield {"type": obj["type"], **vkeyinfo(mapping[vks])}
				continue
		yield obj

list_of_transformations = [
	input(),                                                # libkeyboa
	altgr_workaround_input(),                               # libkeyboa
	enrich_input(),                                         # libkeyboa
	remap(),                                                # layout2
	altgr_workaround_output(),                              # libkeyboa
	output()]                                               # libkeyboa

keyboa_run(list_of_transformations)
