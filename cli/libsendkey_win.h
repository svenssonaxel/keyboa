// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// Legal: See COPYING.txt
#ifndef keyboa_libsendkey_win_h
#define keyboa_libsendkey_win_h

#include "common.h"
#include <stdio.h>
#include "libsendkey.h"

char* sendkey_validate_win(struct keyevent *ke) {
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
	if(ke->win_scancode_present) {
		// scancode 0x21d is for AltGr
		if(!(1<=ke->win_scancode && ke->win_scancode<=0x7f) && ke->win_scancode!=0x21d) {
			return "Invalid scancode";
		}
	}
	//check extended
	if(ke->win_extended_present && ke->win_extended && !ke->win_scancode_present) {
		return "Keyevent cannot have extended flag set without scancode";
	}
	//check virtualkey
	if(ke->win_virtualkey_present) {
		if(!(1<=ke->win_virtualkey && ke->win_virtualkey<=0xfe)) {
			return "Invalid virtualkey";
		}
	}
	//check unicode_codepoint
	if(ke->unicode_codepoint_present) {
		if(ke->win_scancode_present) {
			return "Keyevent cannot have both scancode and unicode_codepoint";
		}
		if(ke->win_virtualkey_present) {
			return "Keyevent cannot have both virtualkey and unicode_codepoint";
		}
		if(!validate_unicode_codepoint(ke->unicode_codepoint)) {
			return "Invalid unicode codepoint";
		}
	}
	else {
		if(!(ke->win_scancode_present || ke->win_virtualkey_present)) {
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
void sendkey_send_win(struct keyevent *ke) {
	//init input structs
	INPUT input[4];
	int idx = 0;
	//init time
	bool calctime = !ke->win_time_present;
	DWORD sendtime = ke->win_time;
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
			bool hw = ke->win_scancode_present;
			mkinput(
				&(input[idx]),
				ke->win_scancode,
				ke->win_virtualkey,
				up,
				hw,
				ke->win_extended,
				false,
				sendtime);
			idx++;
			if(calctime) sendtime++;
		}
	}
	//Send events and handle failure
	if(idx!=SendInput(idx, input, sizeof(INPUT))) {
		fprintf(stderr,
			"Failed sending events\n");
		fflush(stderr);
	}
	maxtime=max(sendtime, maxtime);
}

void sendkey_init_win() {
	global_sendkey_validator = sendkey_validate_win;
	global_sendkey_sender = sendkey_send_win;
}

#endif
