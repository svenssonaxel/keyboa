# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# Legal: See COPYING.txt

VERSION := $(shell ../makeversion)

default: *.py win_vkeys.csv keysyms.csv commonname.csv boxdrawings.csv
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Couldn't determine VERSION. Provide it manually or install git))
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
