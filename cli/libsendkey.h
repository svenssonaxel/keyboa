// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// License: See LICENSE
#ifndef keyboa_libsendkey_h
#define keyboa_libsendkey_h

#ifdef KEYBOA_WIN
#include "common_win.h"
#endif

enum kmevent_type {
	KMEVENT_T_KEYDOWN     = 1,
	KMEVENT_T_KEYUP       = 2,
	KMEVENT_T_KEYPRESS    = 3, //means keydown followed by keyup
	KMEVENT_T_BUTTONDOWN  = 4,
	KMEVENT_T_BUTTONUP    = 5,
	KMEVENT_T_POINTERMOVE = 6,
	KMEVENT_T_WHEEL       = 7,
};
bool kmevent_type_is_kev(enum kmevent_type et) {
	return (et&3)==et;
}
bool kmevent_type_is_mev(enum kmevent_type et) {
	return (et&4)==4;
}

const char *kmevent_type_names[8]={
	NULL,
	"keydown",
	"keyup",
	"keypress",
	"buttondown",
	"buttonup",
	"pointermove",
	"wheel",
};

//Most data structures are Needed by the parser, and therefore cannot be in libsendkey_win.h

enum win_button {
	BUTTON_L  = 0x01,
	BUTTON_R  = 0x02,
	BUTTON_M  = 0x03,
	BUTTON_X1 = 0x05,
	BUTTON_X2 = 0x06,
};

const char *win_button_names[7]={
	NULL, "L", "R", "M", NULL, "X1", "X2",
};

#ifndef KEYBOA_WIN
typedef unsigned long DWORD;
#endif

struct kmevent {
	enum kmevent_type eventtype; bool eventtype_present;
	ucodepoint unicode_codepoint; bool unicode_codepoint_present;
	enum win_button win_button; bool win_button_present;
	bool win_extended; bool win_extended_present;
	signed int win_pointerx_primprim; bool win_pointerx_primprim_present;
	signed int win_pointery_primprim; bool win_pointery_primprim_present;
	signed int win_pointerx_rellegacyacc; bool win_pointerx_rellegacyacc_present;
	signed int win_pointery_rellegacyacc; bool win_pointery_rellegacyacc_present;
	signed int win_pointerx_virtvirt; bool win_pointerx_virtvirt_present;
	signed int win_pointery_virtvirt; bool win_pointery_virtvirt_present;
	DWORD win_scancode; bool win_scancode_present;
	DWORD win_time; bool win_time_present;
	DWORD win_virtualkey; bool win_virtualkey_present;
	signed int win_wheeldeltax; bool win_wheeldeltax_present;
	signed int win_wheeldeltay; bool win_wheeldeltay_present;
};

typedef void (*sendkey_kmevent_handler)(struct kmevent *kme);
sendkey_kmevent_handler global_sendkey_kmevent_handler;

typedef void (*sendkey_error_handler)(bool critical, char* errclass, char* errmsg);
sendkey_error_handler global_sendkey_error_handler;

typedef char* (*sendkey_validator)(struct kmevent *kme);
sendkey_validator global_sendkey_validator;

typedef void (*sendkey_sender)(struct kmevent *kme);
sendkey_sender global_sendkey_sender;

#endif
