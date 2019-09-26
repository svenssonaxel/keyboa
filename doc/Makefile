# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# License: See LICENSE

VERSION := $(shell ../makeversion)

default: listenkey.1 sendkey.1 keyboa.5
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Couldn't determine VERSION. Provide it manually or install git))
	mkdir -p release
	cp $^ release/
	echo === Finished building man pages for keyboa $(VERSION)

clean:
	rm -rf *.[15] *.html *.pdf release/

%.troff: %.scd
	scdoc < $< | sed -r 's/<VERSION>/'"$(VERSION)"'/;' > $@
%.1 %.5: %.troff
	cp $< $@

.PHONY: default clean html pdf
