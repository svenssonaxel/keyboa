# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# License: See LICENSE

CC = i686-w64-mingw32-gcc

ifneq ($(shell echo $${OSTYPE}),cygwin)
$(error Building only supported under Cygwin.)
endif
ifeq (,$(shell which $(CC)))
$(error mingw32 compiler not found. Install cygwin package mingw64-i686-gcc-core)
endif

VERSION = $(shell ./makeversion)
VERSION_H = \#define KEYBOAVERSION "$(VERSION)"

ifneq ($(shell [ -e version.h ] && cat version.h),$(VERSION_H))
$(shell rm version.h)
endif

default: release

clean:
	rm -rf *.exe *.pyc __pycache__/ release/ version.h

release: listenkey.exe sendkey.exe *LICENSE *.py win_vkeys.csv keysyms.csv commonname.csv README.md
	mkdir -p release
	cp $^ release/
	sed -ri 's/<VERSION>/'"$(VERSION)"'/;' release/*.py README.md
	echo === Finished building keyboa version $(VERSION)

listenkey.exe: listenkey.c liblistenkey.h json-str.c common.h version.h
	$(CC) -o listenkey.exe listenkey.c

sendkey.exe: sendkey.c libsendkey.h sendkey-json-parser.c json-str.c common.h version.h jsonsl.c jsonsl.h
	$(CC) -o sendkey.exe sendkey.c

keysyms.csv: keysym/*
	(cd keysym; sed -rf mkcsv.sed *keysym*.h) | sort -g > keysyms.csv

version.h:
	echo '$(VERSION_H)' > version.h

.PHONY: default
