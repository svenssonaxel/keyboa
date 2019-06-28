# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# License: See LICENSE

VERSION = $(shell ./makeversion)

default: release

clean:
	cd windows; make clean
	cd libkeyboa; make clean
	rm -rf __pycache__/ release/

libkeyboa:
	cd libkeyboa; make

windows:
	cd windows; make

release: libkeyboa windows *LICENSE README.md
	mkdir -p release/libkeyboa
	cp -p windows/*.exe *LICENSE README.md layout* release/
	cp -pr libkeyboa/release/* release/libkeyboa
	echo === Finished building keyboa version $(VERSION)

.PHONY: default clean libkeyboa windows
