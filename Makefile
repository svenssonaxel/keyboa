# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# License: See LICENSE

VERSION := $(shell ./makeversion)

default: release

clean:
	cd windows; make clean
	cd libkeyboa; make clean
	cd doc; make clean
	rm -rf __pycache__/ release/

libkeyboa:
	cd libkeyboa; make VERSION=$(VERSION)

windows:
	cd windows; make VERSION=$(VERSION)

doc:
	cd doc; make VERSION=$(VERSION)

release: libkeyboa windows doc *LICENSE README.md
	mkdir -p release/libkeyboa release/man
	cp -pr windows/*.exe *LICENSE README.md layout* release/
	cp -pr libkeyboa/release/* release/libkeyboa
	cp -pr doc/release/*.[15] release/man
	echo === Finished building keyboa version $(VERSION)

.PHONY: default clean libkeyboa windows doc
