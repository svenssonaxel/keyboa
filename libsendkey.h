#ifndef keyboa_win_libsendkey_h
#define keyboa_win_libsendkey_h

#include "common.h"
#include <stdio.h>

enum keyevent_type {
	KEYEVENT_T_UNDEFINED = 0,
	KEYEVENT_T_KEYDOWN = 1,
	KEYEVENT_T_KEYUP = 2,
	KEYEVENT_T_KEYPRESS = 3 //means keydown followed by keyup
};

struct keyevent {
	enum keyevent_type eventtype;
	DWORD scancode;
	DWORD virtualkey;
	bool extended;
	ucodepoint unicode_codepoint;
	DWORD time;
};

typedef void (*sendkey_keyevent_handler)(struct keyevent *ke);
sendkey_keyevent_handler global_sendkey_keyevent_handler;

typedef void (*sendkey_error_handler)(bool critical, char* errclass, char* errmsg);
sendkey_error_handler global_sendkey_error_handler;

char* validate_keyevent(struct keyevent *ke) {
	if(ke->eventtype!=KEYEVENT_T_KEYDOWN &&
	   ke->eventtype!=KEYEVENT_T_KEYUP &&
	   ke->eventtype!=KEYEVENT_T_KEYPRESS) {
		return "Keyevent has erroneous type";
	}
	if(ke->scancode==0 && ke->extended!=false) {
		return "Keyevent cannot have extended flag set without scancode";
		//todo or does it just denote code 256?
	}
	bool is_unicode = (ke->unicode_codepoint!=0);
	if(is_unicode) {
		if(ke->scancode!=0) {
			return "Keyevent cannot have both scancode and unicode_codepoint";
		}
		if(ke->virtualkey!=0) {
			return "Keyevent cannot have both virtualkey and unicode_codepoint";
		}
		if(!validate_unicode_codepoint(ke->unicode_codepoint)) {
			return "Invalid unicode codepoint";
		}
		return 0;
	}
	else {
		if(ke->scancode==0 && ke->virtualkey==0) {
			return "Keyevent must have at least one of scancode, virtualkey, or unicode_codepoint";
		}
		if(ke->virtualkey<0 || 254<ke->virtualkey) {
			return "Invalid virtualkey";
		}
		return 0;
	}
}

//Helper for sending an injected keyboard event.
void sendkbdinput(
	DWORD scancode,
	DWORD virtualkey,
	bool up,
	bool hw,
	bool extended,
	bool unicode,
	DWORD time
) {
	INPUT i;
	i.type = INPUT_KEYBOARD;
	i.ki.wVk = virtualkey;
	i.ki.wScan = scancode;
	i.ki.dwFlags =
		(extended ? KEYEVENTF_EXTENDEDKEY : 0) |
		(up       ? KEYEVENTF_KEYUP       : 0) |
		(unicode  ? KEYEVENTF_UNICODE     : 0) |
		(hw       ? KEYEVENTF_SCANCODE    : 0);
	i.ki.time = time;
	i.ki.dwExtraInfo = 0;
	SendInput(1, &i, sizeof(INPUT));
}

void send_keyevent(struct keyevent *ke) {
	if(ke->eventtype==KEYEVENT_T_KEYPRESS) {
		ke->eventtype=KEYEVENT_T_KEYDOWN;
		send_keyevent(ke);
		ke->eventtype=KEYEVENT_T_KEYUP;
		send_keyevent(ke);
		ke->eventtype=KEYEVENT_T_KEYPRESS;
		return;
	}
	bool up = (ke->eventtype==KEYEVENT_T_KEYUP);
	bool is_unicode = (ke->unicode_codepoint!=0);
	if(is_unicode) {
		ucodepoint cp = ke->unicode_codepoint;
		if(cp & 0x00FF0000) {
			cp -= 0x10000;
			sendkbdinput(0xD800 | (cp >> 10), 0, up, false, false, true, ke->time);
			sendkbdinput(0xDC00 | (cp & 0x3FF), 0, up, false, false, true, ke->time);
		}
		else {
			sendkbdinput(cp, 0, up, false, false, true, ke->time);
		}
	}
	else {
		bool hw = (ke->virtualkey==0);
		sendkbdinput(
			ke->scancode,
			ke->virtualkey,
			up,
			hw,
			ke->extended,
			false,
			ke->time);
	}
}

#endif
