# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# Legal: See COPYING.txt

VERSION := $(shell ./makeversion)

default: release

install:
	install -Dpvt /usr/local/bin release/listenkey.exe
	install -Dpvt /usr/local/bin release/sendkey.exe
	install -Dpvt /usr/lib/python3.6/site-packages/libkeyboa release/libkeyboa/*
	install -Dpvt /usr/lib/python3.7/site-packages/libkeyboa release/libkeyboa/*
	install -Dpvt /usr/local/share/man/man1 release/man/listenkey.1
	install -Dpvt /usr/local/share/man/man1 release/man/sendkey.1
	install -Dpvt /usr/local/share/man/man5 release/man/keyboa.5
	echo Done installing

uninstall:
	rm -rf \
		/usr/local/bin/listenkey.exe \
		/usr/local/bin/sendkey.exe \
		/usr/lib/python3.6/site-packages/libkeyboa \
		/usr/lib/python3.7/site-packages/libkeyboa \
		/usr/local/share/man/man1/listenkey.1 \
		/usr/local/share/man/man1/sendkey.1 \
		/usr/local/share/man/man5/keyboa.5
	echo Done uninstalling

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

release: libkeyboa windows doc *COPYING.txt README.md
	mkdir -p release/libkeyboa release/man release/layout1
	cp -pr windows/*.exe *COPYING.txt README.md layout2.py release/
	cp -pr libkeyboa/release/* release/libkeyboa
	cp -pr doc/release/*.[15] release/man
	cp -pr layout1/*.py layout1/*.csv release/layout1
	echo === Finished building keyboa version $(VERSION)

.PHONY: default install uninstall clean libkeyboa windows doc
