# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# License: See LICENSE

CC = i686-w64-mingw32-gcc

ifneq ($(shell echo $${OSTYPE}),cygwin)
$(error Building only supported under Cygwin.)
endif
ifeq (,$(shell which $(CC)))
$(error mingw32 compiler not found. Install cygwin package mingw64-i686-gcc-core)
endif

VERSION = $(shell ../makeversion)
VERSION_H = \#define KEYBOAVERSION "$(VERSION)"

ifneq ($(shell [ -e version.h ] && cat version.h),$(VERSION_H))
$(shell rm version.h)
endif

default: listenkey.exe sendkey.exe
	echo === Finished building listenkey and sendkey version $(VERSION)

clean:
	rm -rf *.exe version.h

listenkey.exe: listenkey.c liblistenkey.h json-str.c common.h version.h
	$(CC) -o listenkey.exe listenkey.c

sendkey.exe: sendkey.c libsendkey.h sendkey-json-parser.c json-str.c common.h version.h jsonsl/jsonsl.c jsonsl/jsonsl.h
	$(CC) -o sendkey.exe sendkey.c

version.h:
	$(if $(findstring UNKNOWN,$(VERSION)),$(error Couldn't determine VERSION. Provide it manually or install git))
	echo '$(VERSION_H)' > version.h

.PHONY: default clean
