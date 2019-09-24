# Requires python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# License: See LICENSE

import functools

# Run data in series through the supplied list of transformations
def keyboa_run(tr):
	def reducer(reduced, next_generator):
		return next_generator(reduced)
	reduced_transformation = functools.reduce(reducer, tr, [])
	for _ in reduced_transformation:
		pass

import libkeyboa.tr as tr
import libkeyboa.data as data
from libkeyboa.tr import retgen

__all__ = [
	"keyboa_run",
	"tr",
	"data",
	"retgen",
	]
