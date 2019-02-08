#include "common.h"
#include "libsendkey.h"
#include "sendkey-json-parser.c"
#include "sendkey-handlers.c"
#include <stdio.h>

void sendkey_txt_parser() {
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

int main(int argc, char* argv[]) {
	global_sendkey_parser = sendkey_json_parser;
	//global_sendkey_parser = sendkey_txt_parser;
	global_sendkey_keyevent_handler = sendkey_printjson_handler;

	global_sendkey_parser();
}
