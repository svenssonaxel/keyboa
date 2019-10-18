# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# Legal: See COPYING.txt

VERSION := $(shell ../makeversion)
OSTYPE := $(shell echo $${OSTYPE})
ifeq ($(OSTYPE),cygwin)
EXE := .exe
else
EXE :=
endif

ifneq ($(shell [ -e .version ] && cat .version),$(VERSION))
$(shell rm .version)
endif

default: .release

.release: listenkey$(EXE) sendkey$(EXE)
	touch .release
	@echo ━━━┫ Finished building listenkey$(EXE) and sendkey$(EXE) version $(VERSION)

clean:
	rm -rf listenkey sendkey *.exe .dep-* .version .release

listenkey.exe: .dep-mingw64 *listenkey*.[ch] json-str.c common*.h .version
	i686-w64-mingw32-gcc -DKEYBOA_WIN -DKEYBOAVERSION="\"$(VERSION)\"" -o listenkey.exe listenkey.c

listenkey: .dep-gcc *listenkey*.[ch] json-str.c common*.h .version
	gcc -DKEYBOAVERSION="\"$(VERSION)\"" -o listenkey listenkey.c

sendkey.exe: .dep-mingw64 *sendkey*.[ch] json-str.c common*.h .version jsonsl/jsonsl.*
	i686-w64-mingw32-gcc -DKEYBOA_WIN -DKEYBOAVERSION="\"$(VERSION)\"" -o sendkey.exe sendkey.c

sendkey: .dep-gcc *sendkey*.[ch] json-str.c common*.h .version jsonsl/jsonsl.*
	gcc -DKEYBOAVERSION="\"$(VERSION)\"" -o sendkey sendkey.c

.version:
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	echo '$(VERSION)' > .version

.dep-mingw64:
	@if ! which i686-w64-mingw32-gcc; then \
		echo '━━━┓ Missing Mingw-W64.'; \
		echo '   ┃ On Cygwin, install package mingw64-i686-gcc-core'; \
		echo '━━━┛ On Debian, install package gcc-mingw-w64-i686'; \
		false; fi
	touch $@

.dep-gcc:
	@if ! which gcc; then \
		echo '━━━┓ Missing GCC.'; \
		echo '   ┃ On Cygwin: install package gcc-core'; \
		echo '━━━┛ On Debian: apt-get update && apt-get install build-essential'; \
		false; fi
	touch $@

.PHONY: default clean
