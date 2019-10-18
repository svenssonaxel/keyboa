# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# Legal: See COPYING.txt

VERSION := $(shell ../makeversion)

ifneq ($(shell [ -e .version ] && cat .version),$(VERSION))
$(shell rm .version)
endif

MANPAGES := listenkey.1 sendkey.1 keyboa-API.5

default: .release

.release: $(MANPAGES) $(MANPAGES:=.html) $(MANPAGES:=.pdf)
	touch .release
	@echo ━━━┫ Finished building documentation for keyboa $(VERSION)

man: $MANPAGES

html: $(MANPAGES:=.html)

pdf: $(MANPAGES:=.pdf)

clean:
	rm -rf *.[15]* .dep-* .version .release

%.1 %.5: %.scd .dep-scdoc .version
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	./gen $@ man $< "$(VERSION)"

%.1.html %.5.html: %.scd .dep-pandoc template.html .version
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	./gen $@ html $< "$(VERSION)"

%.1.pdf %.5.pdf: %.scd .dep-pandoc .dep-pdflatex .version
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	./gen $@ pdf $< "$(VERSION)"

.version:
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	echo '$(VERSION)' > .version

.dep-scdoc:
	@if ! which scdoc; then \
		echo '━━━┓ Missing scdoc.'; \
		echo '━━━┛ Install scdoc from https://git.sr.ht/~sircmpwn/scdoc'; \
		false; fi
	touch $@

.dep-pdflatex:
	@if ! which pdflatex; then \
		echo '━━━┓ Missing pdflatex.'; \
		echo '   ┃ On Cygwin, install the following packages:'; \
		echo '   ┃ - texlive-collection-latex'; \
		echo '   ┃ - texlive-collection-fontsrecommended'; \
		echo '   ┃ - texlive-collection-latexrecommended'; \
		echo '━━━┛ On Debian: apt-get update && apt-get install texlive'; \
		false; fi
	@if ! kpsewhich xcolor.sty; then \
		echo '━━━┓ Missing xcolor.sty.'; \
		echo '   ┃ On Cygwin, install package texlive-collection-latexrecommended'; \
		echo '━━━┛ On Debian: apt-get update && apt-get install texlive'; \
		false; fi
	@if ! kpsewhich lmodern.sty; then \
		echo '━━━┓ Missing lmodern.sty.'; \
		echo '   ┃ On Cygwin, install package texlive-collection-fontsrecommended'; \
		echo '━━━┛ On Debian: apt-get update && apt-get install texlive'; \
		false; fi
	touch $@

.dep-pandoc:
	@if ! which pandoc; then \
		echo '━━━┓ Missing pandoc.'; \
		echo '   ┃ On Cygwin: download pandoc-...-windows-i386.zip from'; \
		echo '   ┃  https://github.com/jgm/pandoc/releases/ then:'; \
		echo '   ┃   unzip pandoc*.zip'; \
		echo '   ┃   chmod a+x pandoc*/pandoc.exe'; \
		echo '   ┃   mv pandoc*/pandoc.exe /bin/'; \
		echo '━━━┛ On Debian: apt-get update && apt-get install pandoc'; \
		false; fi
	touch $@

.PHONY: default clean man html pdf
