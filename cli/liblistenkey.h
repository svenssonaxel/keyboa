// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// License: See LICENSE
#include "common.h"
#include <stdio.h>

void quitlistenkey() {
#ifdef KEYBOA_WIN
	if(opt_w)
		quitlistenkey_win();
#endif
}
