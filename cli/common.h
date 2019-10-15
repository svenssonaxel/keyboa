// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// Legal: See COPYING.txt
#ifndef keyboa_common_h
#define keyboa_common_h

#include <stdbool.h>
#include <stdint.h>

#define LEN(a) (sizeof(a) / sizeof(a)[0])

typedef uint32_t ucodepoint;

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
