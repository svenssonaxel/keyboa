#include "libsendkey.h"

int main(int argc, char* argv[]) {
	DWORD code;
	char ch[6];
	BOOL up;
	while(scanf("%1[ud]%1[vseu]%x%1[\n]", ch, ch+2, &code, ch+4) == 4) {
		up = ch[0] == 'u';
		printf("got: {up:%c, type:%c, code:%x}\n", up ? 'u' : 'd', ch[2], code);
		switch(ch[2]) {
			case 's': sendhwkey(code, 0, up); break;
			case 'e': sendhwkey(code, 1, up); break;
			case 'v': sendvkey(code, up); break;
			case 'u': sendunicodekey(code, up); break;
			default: abort();
		}
	}
}
