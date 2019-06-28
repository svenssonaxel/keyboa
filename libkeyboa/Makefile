# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# License: See LICENSE

VERSION = $(shell ../makeversion)

default: *.py win_vkeys.csv keysyms.csv commonname.csv
	mkdir -p release
	cp $^ release/
	sed -ri 's/<VERSION>/'"$(VERSION)"'/;' release/*.py release/*.csv
	echo === Finished building libkeyboa version $(VERSION)

clean:
	rm -rf *.pyc __pycache__/ keysyms.csv release/

keysyms.csv: keysym/*
	(echo '# This file is part of keyboa version <VERSION>'; \
	 (cd keysym; sed -rf mkcsv.sed *keysym*.h) | sort -g) > keysyms.csv

.PHONY: default clean
