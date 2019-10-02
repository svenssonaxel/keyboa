// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// License: See LICENSE
#ifndef keyboa_common_h
#define keyboa_common_h

#include <stdbool.h>
#include <stdint.h>

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
