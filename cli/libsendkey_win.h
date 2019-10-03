// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// Legal: See COPYING.txt
#ifndef keyboa_libsendkey_win_h
#define keyboa_libsendkey_win_h

#include "common.h"
#include <stdio.h>
#include "libsendkey.h"

#ifndef MOUSEEVENTF_HWHEEL
#define MOUSEEVENTF_HWHEEL 0x01000
#endif

char* sendkey_validate_win(struct kmevent *kme) {
	//check eventtype
	if(!kme->eventtype_present) {
		return "Missing type field";
	}
	enum kmevent_type t=kme->eventtype;
	//check type
	if(!(
		 0<t && t<(sizeof(kmevent_type_names)/sizeof(char*)) &&
		 kmevent_type_names[t]!=NULL))
		return "Unknown type";
	bool is_kev = kmevent_type_is_kev(t);
	bool is_mev = kmevent_type_is_mev(t);
	//check unicode_codepoint
	if(is_kev && kme->unicode_codepoint_present &&
	   !validate_unicode_codepoint(kme->unicode_codepoint)) {
		return "Invalid unicode codepoint";
	}
	//check win_button
	if(t==KMEVENT_T_BUTTONDOWN ||
	   t==KMEVENT_T_BUTTONUP) {
		if(!kme->win_button_present)
			return "Missing win_button";
		if(!win_button_names[kme->win_button])
			return "Invalid win_button";
	}
	//check win_coord_system
	if(t==KMEVENT_T_POINTERMOVE) {
		if(!kme->win_coord_system_present)
			return "win_coord_system is required in pointermove events";
		if(kme->win_coord_system==0 ||
		   kme->win_coord_system==COORD_SYSTEM_ABS_PIXELACTUAL)
			return "Unsupported win_coord_system";
	}
	//check win_extended
	if(is_kev &&
	   kme->win_extended_present &&
	   kme->win_extended &&
	   !kme->win_scancode_present) {
		return "Keyevent cannot have extended flag set without scancode";
	}
	//no need to check win_pointerx, win_pointery
	//check win_scancode
	if(is_kev && kme->win_scancode_present) {
		// scancode 0x21d is for AltGr
		if(!(1<=kme->win_scancode && kme->win_scancode<=0x7f) && kme->win_scancode!=0x21d) {
			return "Invalid win_scancode";
		}
	}
	//no need to check win_time since no invalid state is representable
	//check win_virtualkey
	if(is_kev && kme->win_virtualkey_present) {
		if(!(1<=kme->win_virtualkey && kme->win_virtualkey<=0xfe)) {
			return "Invalid win_virtualkey";
		}
	}
	if(is_kev &&
	   !kme->unicode_codepoint_present &&
	   !kme->win_scancode_present &&
	   !kme->win_virtualkey_present)
		return "Keyevent must have at least one of unicode_codepoint, scancode or virtualkey ";
	//check win_wheeldeltax, win_wheeldeltay
	if(t==KMEVENT_T_WHEEL) {
		bool xp=kme->win_wheeldeltax_present;
		bool yp=kme->win_wheeldeltay_present;
		if(!xp && !yp)
			return "Either win_wheeldeltax or win_wheeldeltay required in wheel events";
		if(xp && yp)
			return "Only one of win_wheeldeltax and win_wheeldeltay can be present in wheel events";
		if(xp) {
			if(kme->win_wheeldeltax < -12000 || 12000 < kme->win_wheeldeltax)
				return "win_wheeldeltax out of bounds (-12000, 12000)";
		}
		if(yp) {
			if(kme->win_wheeldeltay < -12000 || 12000 < kme->win_wheeldeltay)
				return "win_wheeldeltay out of bounds (-12000, 12000)";
		}
	}
	return 0;
}

//Helper for sending injected keyboard events
void mkinput_k(
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

//Function for sending injected keyboard events
void sendkey_send_win_k(struct kmevent *kme) {
	//init input structs
	INPUT input[4];
	int idx = 0;
	//init time
	bool calctime = !kme->win_time_present;
	DWORD sendtime = kme->win_time;
	if(calctime) {
		sendtime=max(GetTickCount(), maxtime+1);
	}
	//prepare input structs
	for(int k=0;k<2;k++) {
		bool up = k==1;
		if(!up && kme->eventtype==KMEVENT_T_KEYUP) continue;
		if(up && kme->eventtype==KMEVENT_T_KEYDOWN) continue;
		if(kme->unicode_codepoint_present) {
			ucodepoint cp = kme->unicode_codepoint;
			if(cp & 0x00FF0000) {
				cp -= 0x10000;
				mkinput_k(&(input[idx]), 0xD800 | (cp >> 10), 0, up, false, false, true, sendtime);
				idx++;
				if(calctime) sendtime++;
				mkinput_k(&(input[idx]), 0xDC00 | (cp & 0x3FF), 0, up, false, false, true, sendtime);
				idx++;
				if(calctime) sendtime++;
			}
			else {
				mkinput_k(&(input[idx]), cp, 0, up, false, false, true, sendtime);
				idx++;
				if(calctime) sendtime++;
			}
		}
		else {
			bool hw = kme->win_scancode_present;
			mkinput_k(
				&(input[idx]),
				kme->win_scancode,
				kme->win_virtualkey,
				up,
				hw,
				kme->win_extended,
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

//Function for sending injected mouse events
void sendkey_send_win_m(struct kmevent *kme) {
	INPUT i;
	bool calctime = !kme->win_time_present;
	DWORD sendtime = kme->win_time;
	if(calctime) {
		sendtime=max(GetTickCount(), maxtime+1);
	}
	i.type = INPUT_MOUSE;
	// initialization
	i.mi.dx = 0;
	i.mi.dy = 0;
	i.mi.mouseData = 0;
	i.mi.dwFlags = 0;
	i.mi.time = 0;
	i.mi.dwExtraInfo = 0;
	// populate depending on event type
	switch(kme->eventtype) {
	case KMEVENT_T_BUTTONDOWN:
		switch(kme->win_button) {
		case BUTTON_L:  i.mi.dwFlags |= MOUSEEVENTF_LEFTDOWN; break;
		case BUTTON_R:  i.mi.dwFlags |= MOUSEEVENTF_RIGHTDOWN; break;
		case BUTTON_M:  i.mi.dwFlags |= MOUSEEVENTF_MIDDLEDOWN; break;
		case BUTTON_X1: i.mi.dwFlags |= MOUSEEVENTF_XDOWN;
			i.mi.mouseData = XBUTTON1; break;
		case BUTTON_X2: i.mi.dwFlags |= MOUSEEVENTF_XDOWN;
			i.mi.mouseData = XBUTTON2; break;
		}
		break;
	case KMEVENT_T_BUTTONUP:
		switch(kme->win_button) {
		case BUTTON_L:  i.mi.dwFlags |= MOUSEEVENTF_LEFTUP; break;
		case BUTTON_R:  i.mi.dwFlags |= MOUSEEVENTF_RIGHTUP; break;
		case BUTTON_M:  i.mi.dwFlags |= MOUSEEVENTF_MIDDLEUP; break;
		case BUTTON_X1: i.mi.dwFlags |= MOUSEEVENTF_XUP;
			i.mi.mouseData = XBUTTON1; break;
		case BUTTON_X2: i.mi.dwFlags |= MOUSEEVENTF_XUP;
			i.mi.mouseData = XBUTTON2; break;
		}
		break;
	case KMEVENT_T_POINTERMOVE:
		i.mi.dwFlags |= MOUSEEVENTF_MOVE;
		i.mi.dx = kme->win_pointerx;
		i.mi.dy = kme->win_pointery;
		switch(kme->win_coord_system) {
		case COORD_SYSTEM_ABS_NORMPRIMARY:
			i.mi.dwFlags |= MOUSEEVENTF_ABSOLUTE;
			break;
		case COORD_SYSTEM_ABS_NORMVIRTUAL:
			i.mi.dwFlags |= MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK;
			break;
		case COORD_SYSTEM_REL_PIXELSCALED:
			//no flags necessary
			break;
		}
		break;
	case KMEVENT_T_WHEEL:
			if(kme->win_wheeldeltax_present) {
				i.mi.mouseData = kme->win_wheeldeltax_present;
				i.mi.dwFlags |= MOUSEEVENTF_HWHEEL;
			}
			if(kme->win_wheeldeltay_present) {
				i.mi.mouseData = kme->win_wheeldeltay_present;
				i.mi.dwFlags |= MOUSEEVENTF_WHEEL;
			}
		break;
	}
	//Send events and handle failure
	i.mi.time = sendtime;
	if(1!=SendInput(1, &i, sizeof(INPUT))) {
		fprintf(stderr,
			"Failed sending events\n");
		fflush(stderr);
	}
	if(calctime) sendtime++;
	maxtime=max(sendtime, maxtime);
}

void sendkey_send_win(struct kmevent *kme) {
	if(kmevent_type_is_kev(kme->eventtype))
		sendkey_send_win_k(kme);
	if(kmevent_type_is_mev(kme->eventtype))
		sendkey_send_win_m(kme);
}

void sendkey_init_win() {
	global_sendkey_validator = sendkey_validate_win;
	global_sendkey_sender = sendkey_send_win;
}

#endif
