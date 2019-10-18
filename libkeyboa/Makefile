# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# Legal: See COPYING.txt

VERSION := $(shell ../makeversion)

ifneq ($(shell [ -e .version ] && cat .version),$(VERSION))
$(shell rm .version)
endif

default: .release

.release: *.py win_vkeys.csv keysyms.csv commonname.csv boxdrawings.csv .version
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	rm -rf release/
	mkdir -p release
	cp *.py *.csv release/
	sed -ri 's/<VERSION>/'"$(VERSION)"'/;' release/*.py release/*.csv
	touch .release
	@echo ━━━┫ Finished building libkeyboa version $(VERSION)

clean:
	rm -rf *.pyc __pycache__/ keysyms.csv release/ .version .release

keysyms.csv: keysym/*
	(echo '# This file is part of keyboa version <VERSION>'; \
	 (cd keysym; sed -rf mkcsv.sed *keysym*.h) | sort -g) > keysyms.csv

.version:
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	echo '$(VERSION)' > .version

.PHONY: default clean
