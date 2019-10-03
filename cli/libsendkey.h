// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// License: See LICENSE
#ifndef keyboa_libsendkey_h
#define keyboa_libsendkey_h

#ifdef keyboa_win
#include "common_win.h"
#endif

enum keyevent_type {
	KEYEVENT_T_UNDEFINED = 0,
	KEYEVENT_T_KEYDOWN = 1,
	KEYEVENT_T_KEYUP = 2,
	KEYEVENT_T_KEYPRESS = 3 //means keydown followed by keyup
};

#ifndef keyboa_win
typedef unsigned long DWORD;
#endif

struct keyevent {
	enum keyevent_type eventtype; bool eventtype_present;
	DWORD win_scancode; bool win_scancode_present;
	bool win_extended; bool win_extended_present;
	DWORD win_virtualkey; bool win_virtualkey_present;
	ucodepoint unicode_codepoint; bool unicode_codepoint_present;
	DWORD win_time; bool win_time_present;
};

typedef void (*sendkey_keyevent_handler)(struct keyevent *ke);
sendkey_keyevent_handler global_sendkey_keyevent_handler;

typedef void (*sendkey_error_handler)(bool critical, char* errclass, char* errmsg);
sendkey_error_handler global_sendkey_error_handler;

typedef char* (*sendkey_validator)(struct keyevent *ke);
sendkey_validator global_sendkey_validator;

typedef void (*sendkey_sender)(struct keyevent *ke);
sendkey_sender global_sendkey_sender;

#endif
