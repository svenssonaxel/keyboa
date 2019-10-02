// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// License: See LICENSE
#ifndef keyboa_common_h
#define keyboa_common_h

#define WINVER 0x0500
#include <windows.h>

#include <stdbool.h>

#ifndef LLKHF_LOWER_IL_INJECTED
#define LLKHF_LOWER_IL_INJECTED 0x02
#endif

#ifndef WM_MOUSEHWHEEL
#define WM_MOUSEHWHEEL 0x020E
#endif

#ifndef LLMHF_LOWER_IL_INJECTED
#define LLMHF_LOWER_IL_INJECTED 0x00000002
#endif

typedef unsigned __int32 ucodepoint;

bool validate_unicode_codepoint(ucodepoint cp) {
	//Too high codes are invalid
	if(cp>((ucodepoint)0x10FFFF)) {
		return false;
	}
	//Surrogate codes (U+D800 - U+DFFF) are invalid
	ucodepoint mask = 0x1FF800;
	ucodepoint surr = 0x00D800;
	if(mask&cp==surr) {
		return false;
	}
	//this is probably incorrect but sufficient.
	return true;
}

#endif
