# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# License: See LICENSE

ifneq ($(shell echo $${OSTYPE}),cygwin)
$(error Building only supported under Cygwin.)
endif
ifeq (,$(shell which i686-w64-mingw32-gcc))
$(error mingw32 compiler not found. Install cygwin package mingw64-i686-gcc-core)
endif

VERSION = $(shell ./makeversion)

default: release

clean:
	rm -rf *.exe *.pyc __pycache__/ release/ version.h

release: listenkey.exe sendkey.exe *LICENSE *.py README.md
	mkdir -p release
	cp $^ release/
	sed -ri 's/<VERSION>/'"$(VERSION)"'/;' release/*.py README.md
	echo === Finished building keyboa version $(VERSION)

listenkey.exe: listenkey.c liblistenkey.h json-str.c common.h version.h
	i686-w64-mingw32-gcc -o listenkey.exe listenkey.c

sendkey.exe: sendkey.c libsendkey.h sendkey-json-parser.c json-str.c common.h version.h
	i686-w64-mingw32-gcc -o sendkey.exe sendkey.c

version.h:
	echo '#define KEYBOAVERSION "'$(VERSION)'"' > version.h

.PHONY: default
