# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# License: See LICENSE

VERSION := $(shell ../makeversion)

default: listenkey.1 sendkey.1 keyboa.5
	mkdir -p release
	cp $^ release/
	echo === Finished building man pages for keyboa $(VERSION)

clean:
	rm -rf *.[15] *.html *.pdf release/

%.troff: %.scd dep-scdoc
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	scdoc < $< | sed -r 's/<VERSION>/'"$(VERSION)"'/;' > $@
%.1 %.5: %.troff
	cp $< $@

dep-scdoc:
	@if which scdoc; then echo found scdoc compiler; else \
		echo Missing scdoc.; \
		echo Install scdoc from https://git.sr.ht/~sircmpwn/scdoc; \
		false; fi


.PHONY: dep-scdoc default clean html pdf
