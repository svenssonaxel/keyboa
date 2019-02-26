# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>

default: listenkey.exe sendkey.exe

clean:
	rm -rf *.exe *.pyc __pycache__/ release/

release: listenkey.exe sendkey.exe *.py
	mkdir -p release
	cp $^ release/

listenkey.exe: listenkey.c liblistenkey.h json-str.c common.h
	i686-w64-mingw32-gcc -o listenkey.exe listenkey.c

sendkey.exe: sendkey.c libsendkey.h sendkey-json-parser.c json-str.c common.h
	i686-w64-mingw32-gcc -o sendkey.exe sendkey.c

.PHONY: default
