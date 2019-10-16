# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# Legal: See COPYING.txt

VERSION := $(shell ../makeversion)

default: man html pdf
	echo === Finished building documentation for keyboa $(VERSION)

man: listenkey.1 sendkey.1 keyboa.5

html: listenkey.1.html sendkey.1.html keyboa.5.html

pdf: listenkey.1.pdf sendkey.1.pdf keyboa.5.pdf

clean:
	rm -rf *.[15] *.[15].html *.[15].pdf

%.1 %.5: %.scd dep-scdoc
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	./gen $@ man $< "$(VERSION)"

%.1.html %.5.html: %.scd dep-markdown prelude.html
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	./gen $@ html $< "$(VERSION)"

%.pdf: %.html dep-pandoc
	pandoc -o $@ $<

dep-scdoc:
	@if which scdoc; then echo found scdoc compiler; else \
		echo Missing scdoc.; \
		echo Install scdoc from https://git.sr.ht/~sircmpwn/scdoc; \
		false; fi

dep-markdown:
	@if which markdown; then echo found markdown; else \
		echo Missing markdown.; \
		echo On Cygwin, install package todo; \
		echo On Debian: apt-get update && apt-get install markdown; \
		false; fi

dep-pandoc:
	@if which pandoc; then echo found pandoc; else \
		echo Missing pandoc.; \
		echo On Cygwin, install package todo; \
		echo On Debian: apt-get update && apt-get install pandoc; \
		false; fi

.PHONY: dep-scdoc dep-markdown dep-pandoc default clean man html pdf
