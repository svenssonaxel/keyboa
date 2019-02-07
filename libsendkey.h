#include "common.h"
#include <stdio.h>

//Send an injected keyboard event.
void sendkbdinput(
	DWORD scancode,
	DWORD virtualkey,
	BOOL up,
	BOOL hw,
	BOOL extended,
	BOOL unicode
) {
	INPUT i;
	i.type = INPUT_KEYBOARD;
	i.ki.wVk = virtualkey;
	i.ki.wScan = scancode;
	i.ki.dwFlags =
		(hw       ? KEYEVENTF_SCANCODE    : 0) |
		(up       ? KEYEVENTF_KEYUP       : 0) |
		(extended ? KEYEVENTF_EXTENDEDKEY : 0) |
		(unicode  ? KEYEVENTF_UNICODE     : 0);
	i.ki.time = 0;
	i.ki.dwExtraInfo = 0;
	SendInput(1, &i, sizeof(INPUT));
}

//Send a keyboard event defined by virtual key
void sendvkey(DWORD virtualkey, BOOL up) {
	sendkbdinput(0, virtualkey, up, 0, 0, 0);  //todo: lookup scancode
}

//Send a keyboard event defined by scancode
void sendhwkey(DWORD scancode, BOOL extended, BOOL up) {
	sendkbdinput(scancode, 0, up, 1, extended, 0);
}

//Send a unicode key event
void sendunicodekey(DWORD unicode, BOOL up) {
	if(unicode & 0x00FF0000) {
		unicode -= 0x10000;
		sendkbdinput(0xD800 | (unicode >> 10), 0, up, 0, 0, 1);
		sendkbdinput(0xDC00 | (unicode & 0x3FF), 0, up, 0, 0, 1);
	}
	else {
		sendkbdinput(unicode, 0, up, 0, 0, 1);
	}
}
