#ifndef keyboa_win_common_h
#define keyboa_win_common_h

#define WINVER 0x0500
#include <windows.h>

typedef unsigned __int8 bool;
#define true ((bool)(1==1))
#define false ((bool)(1==0))

#ifndef LLKHF_LOWER_IL_INJECTED
#define LLKHF_LOWER_IL_INJECTED 0x02
#endif

#endif
