# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# License: See LICENSE

VERSION := $(shell ../makeversion)
VERSION_H = \#define KEYBOAVERSION "$(VERSION)"
EXE := $(if $(eq $(OSTYPE),cygwin),.exe,)

ifneq ($(shell [ -e version.h ] && cat version.h),$(VERSION_H))
$(shell rm version.h)
endif

default: listenkey$(EXE) sendkey$(EXE)
	echo === Finished building listenkey$(EXE) and sendkey$(EXE) version $(VERSION)

clean:
	rm -rf listenkey sendkey *.exe version.h

listenkey.exe: dep-mingw64 *listenkey*.[ch] json-str.c common*.h version.h
	i686-w64-mingw32-gcc -Dkeyboa_win -o listenkey.exe listenkey.c

listenkey: dep-gcc *listenkey*.[ch] json-str.c common*.h version.h
	gcc -o listenkey listenkey.c

sendkey.exe: dep-mingw64 *sendkey*.[ch] json-str.c common*.h version.h jsonsl/jsonsl.*
	i686-w64-mingw32-gcc -Dkeyboa_win -o sendkey.exe sendkey.c

sendkey: dep-gcc *sendkey*.[ch] json-str.c common*.h version.h jsonsl/jsonsl.*
	gcc -o sendkey sendkey.c

version.h:
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Could not determine VERSION. Provide it manually or install git))
	echo '$(VERSION_H)' > version.h

dep-mingw64:
	@if which i686-w64-mingw32-gcc; then echo found mingw64 compiler; else \
		echo Missing Mingw-W64.; \
		echo On Cygwin, install package mingw64-i686-gcc-core.; \
		echo On Debian, install package gcc-mingw-w64-i686.; \
		false; fi

dep-gcc:
	@if which gcc; then echo found gcc compiler; else \
		echo Missing GCC.; \
		echo On Cygwin, install package gcc-core.; \
		echo On Debian, install package build-essential.; \
		false; fi

.PHONY: default clean dep-mingw64 dep-gcc
