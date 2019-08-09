// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// License: See LICENSE
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
	enum keyevent_type eventtype; bool eventtype_present;
	DWORD scancode; bool scancode_present;
	bool extended; bool extended_present;
	DWORD virtualkey; bool virtualkey_present;
	ucodepoint unicode_codepoint; bool unicode_codepoint_present;
	DWORD time; bool time_present;
};

typedef void (*sendkey_keyevent_handler)(struct keyevent *ke);
sendkey_keyevent_handler global_sendkey_keyevent_handler;

typedef void (*sendkey_error_handler)(bool critical, char* errclass, char* errmsg);
sendkey_error_handler global_sendkey_error_handler;

char* validate_keyevent(struct keyevent *ke) {
	//check eventtype
	if(!ke->eventtype_present) {
		return "Missing type field";
	}
	if(ke->eventtype!=KEYEVENT_T_KEYDOWN &&
	   ke->eventtype!=KEYEVENT_T_KEYUP &&
	   ke->eventtype!=KEYEVENT_T_KEYPRESS) {
		return "Unknown type";
	}
	//check scancode
	if(ke->scancode_present) {
		if(!(1<=ke->scancode && ke->scancode<=255)) { //todo check doc
			return "Invalid scancode";
		}
	}
	//check extended
	if(ke->extended_present && ke->extended && !ke->scancode_present) {
		return "Keyevent cannot have extended flag set without scancode";
	}
	//check virtualkey
	if(ke->virtualkey_present) {
		if(!(0<=ke->virtualkey && ke->virtualkey<=254)) { //todo check doc
			return "Invalid virtualkey";
		}
	}
	//check unicode_codepoint
	if(ke->unicode_codepoint_present) {
		if(ke->scancode_present) {
			return "Keyevent cannot have both scancode and unicode_codepoint";
		}
		if(ke->virtualkey_present) {
			return "Keyevent cannot have both virtualkey and unicode_codepoint";
		}
		if(!validate_unicode_codepoint(ke->unicode_codepoint)) {
			return "Invalid unicode codepoint";
		}
	}
	else {
		if(!(ke->scancode_present || ke->virtualkey_present)) {
			return "Keyevent must have at least one of scancode, virtualkey, or unicode_codepoint";
		}
	}
	return 0;
	//no need to check time since no invalid state is representable
}

//Helper for sending an injected keyboard event.
void mkinput(
	INPUT* i,
	DWORD scancode,
	DWORD virtualkey,
	bool up,
	bool hw,
	bool extended,
	bool unicode,
	DWORD time
) {
	i->type = INPUT_KEYBOARD;
	i->ki.wVk = virtualkey;
	i->ki.wScan = scancode;
	i->ki.dwFlags =
		(extended ? KEYEVENTF_EXTENDEDKEY : 0) |
		(up       ? KEYEVENTF_KEYUP       : 0) |
		(unicode  ? KEYEVENTF_UNICODE     : 0) |
		(hw       ? KEYEVENTF_SCANCODE    : 0);
	i->ki.time = time;
	i->ki.dwExtraInfo = 0;
}

DWORD maxtime = 0;
void send_keyevent(struct keyevent *ke) {
	//init input structs
	INPUT input[4];
	int idx = 0;
	//init time
	bool calctime = !ke->time_present;
	DWORD sendtime = ke->time;
	if(calctime) {
		sendtime=max(GetTickCount(), maxtime+1);
	}
	//prepare input structs
	for(int k=0;k<2;k++) {
		bool up = k==1;
		if(!up && ke->eventtype==KEYEVENT_T_KEYUP) continue;
		if(up && ke->eventtype==KEYEVENT_T_KEYDOWN) continue;
		if(ke->unicode_codepoint_present) {
			ucodepoint cp = ke->unicode_codepoint;
			if(cp & 0x00FF0000) {
				cp -= 0x10000;
				mkinput(&(input[idx]), 0xD800 | (cp >> 10), 0, up, false, false, true, sendtime);
				idx++;
				if(calctime) sendtime++;
				mkinput(&(input[idx]), 0xDC00 | (cp & 0x3FF), 0, up, false, false, true, sendtime);
				idx++;
				if(calctime) sendtime++;
			}
			else {
				mkinput(&(input[idx]), cp, 0, up, false, false, true, sendtime);
				idx++;
				if(calctime) sendtime++;
			}
		}
		else {
			bool hw = ke->scancode_present;
			mkinput(
				&(input[idx]),
				ke->scancode,
				ke->virtualkey,
				up,
				hw,
				ke->extended,
				false,
				sendtime);
			idx++;
			if(calctime) sendtime++;
		}
	}
	SendInput(idx, input, sizeof(INPUT));
	//todo handle return value
	maxtime=max(sendtime, maxtime);
}

#endif
