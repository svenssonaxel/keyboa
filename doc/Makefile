# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# Legal: See COPYING.txt

VERSION := $(shell ../makeversion)

ifneq ($(shell [ -e .version ] && cat .version),$(VERSION))
$(shell rm .version)
endif

MANPAGES := listenkey.1 sendkey.1 keyboa.5

default: .release

.release: $(MANPAGES) $(MANPAGES:=.html) $(MANPAGES:=.pdf)
	touch .release
	@echo === Finished building documentation for keyboa $(VERSION)

man: $MANPAGES

html: $(MANPAGES:=.html)

pdf: $(MANPAGES:=.pdf)

clean:
	rm -rf *.[15] *.[15].html *.[15].pdf .dep-* .version .release

%.1 %.5: %.scd .dep-scdoc .version
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	./gen $@ man $< "$(VERSION)"

%.1.html %.5.html: %.scd .dep-markdown prelude.html .version
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	./gen $@ html $< "$(VERSION)"

%.pdf: %.html .dep-pandoc
	pandoc -o $@ $<

.version:
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	echo '$(VERSION)' > .version

.dep-scdoc:
	@if which scdoc; then echo found scdoc compiler; touch $@; else \
		echo Missing scdoc.; \
		echo Install scdoc from https://git.sr.ht/~sircmpwn/scdoc; \
		false; fi

.dep-markdown:
	@if which markdown; then echo found markdown; touch $@; else \
		echo Missing markdown.; \
		echo On Cygwin, install package todo; \
		echo On Debian: apt-get update && apt-get install markdown; \
		false; fi

.dep-pandoc:
	@if which pandoc; then echo found pandoc; touch $@; else \
		echo Missing pandoc.; \
		echo On Cygwin, install package todo; \
		echo On Debian: apt-get update && apt-get install pandoc; \
		false; fi

.PHONY: default clean man html pdf
