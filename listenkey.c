// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// License: See LICENSE
#include <unistd.h>
#include <stdio.h>
#include <signal.h>
#include "common.h"
#include "liblistenkey.h"

bool opt_c, opt_C, opt_i, opt_e, opt_d, opt_f, opt_l, opt_L;
int evcount;

bool processevent(KBDLLHOOKSTRUCT* hooked) {
	DWORD     virtualkey = hooked->vkCode;
	DWORD     scancode = hooked->scanCode;
	DWORD     flags = hooked->flags;
	DWORD     time = hooked->time;
	bool consume =
		(opt_c && !(flags & LLKHF_INJECTED)) ||
		(opt_C && (flags & LLKHF_INJECTED));
	if(!opt_i && (flags & LLKHF_INJECTED)) {
		return consume;
	}
	if(!opt_f) {
		printf(
			"{\"type\":%s"
			",\"win_scancode\":%5u"
			",\"win_virtualkey\":%3u"
			",\"win_extended\":%s"
			",\"win_injected\":%s"
			",\"win_lower_il_injected\":%s"
			",\"win_altdown\":%s"
			",\"win_time\":%10u}"
			,(flags & LLKHF_UP) ? "\"keyup\"  " : "\"keydown\""
			,scancode
			,virtualkey
			,(flags & LLKHF_EXTENDED) ? "true " : "false"
			,(flags & LLKHF_INJECTED) ? "true " : "false"
			,(flags & LLKHF_LOWER_IL_INJECTED) ? "true " : "false"
			,(flags & LLKHF_ALTDOWN) ? "true " : "false"
			,time
		);
	}
	if(opt_f) {
		printf("%s %04x %02x %s%s%s%s %08x"
			,(flags & LLKHF_UP) ? "u" : "d"
			,scancode
			,virtualkey
			,(flags & LLKHF_EXTENDED) ? "e" : "-"
			,(flags & LLKHF_INJECTED) ? "i" : "-"
			,(flags & LLKHF_LOWER_IL_INJECTED) ? "l" : "-"
			,(flags & LLKHF_ALTDOWN) ? "a" : "-"
			,time
		);
	}
	if(printf("\n") == -1) {
		quitlistenkey();
	}
	fflush(stdout);
	if(opt_d) {
		if(++evcount>20) {
			quitlistenkey();
		}
	}
	if(opt_e) {
		if(scancode == 1 && flags == 128) {
			quitlistenkey();
		}
	}
	return consume;
}

void printinit(FILE* stream) {
	fprintf(stream, "{\"type\":\"init\",\"platform\":\"windows\"");

	//Retrieve current state for virtualkeys
	//https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getasynckeystate
	{
		fprintf(stream, ",\"vkeysdown\":[");
		bool first=true;
		for(int i=1; i<=254; i++) {
			if(GetAsyncKeyState(i)>>8) {
				fprintf(stream, "%s%u", first?"":",", i);
				first=false;
			}
		}
		fprintf(stream, "]");
	}

	//Retrieve OEMCP
	//https://docs.microsoft.com/en-us/windows/desktop/api/winnls/nf-winnls-getoemcp
	fprintf(stream, ",\"OEMCP\":%u", GetOEMCP());

	//Retrieve active input locale identifier (formerly called the keyboard layout) for current thread
	//https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getkeyboardlayout
	fprintf(stream, ",\"active_input_locale_current_thread\":%u", GetKeyboardLayout(0));

	//Retrieve available input locale identifiers (formerly called keyboard layout handles)
	//https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getkeyboardlayoutlist
	{
		int noflocales = GetKeyboardLayoutList(0, 0);
		if(noflocales) {
			HKL* lpList = malloc(noflocales * sizeof(HKL));
			GetKeyboardLayoutList(noflocales, lpList);
			fprintf(stream, ",\"available_input_locales\":[");
			bool first=true;
			for(int i=0; i<noflocales; i++) {
				fprintf(stream, "%s%u", first?"":",", lpList[i]);
				first=false;
			}
			fprintf(stream, "]");
			free(lpList);
		}
	}


	//Retrieve keyboard type, subtype, and number of function keys
	//https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getkeyboardtype
	fprintf(stream, ",\"keyboard_type\":%u", GetKeyboardType(0));
	fprintf(stream, ",\"keyboard_subtype\":%u", GetKeyboardType(1));
	fprintf(stream, ",\"function_keys\":%u", GetKeyboardType(2));

	//Retrieve the name of keys (scancode)
	//https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getkeynametexta
	{
		fprintf(stream, ",\"key_names\":[");
		bool first=true;
		char keyname[1000];
		char keyname_json[6000];
		int namelen;
		for(int extended=0; extended<2; extended++) {
			for(int scancode=0; scancode<256; scancode++) {
				namelen = GetKeyNameTextA(
					(scancode << 16) |
					(extended << 24),
					keyname,
					1000);
				if(namelen) {
					if(!latin1_string_to_json(keyname, keyname_json)){fprintf(stream,"\nerror latin1\n");}
					fprintf(stream, "%s{\"scancode\":%u,\"extended\":%s,\"keyname\":\"%s\"}",
						first?"":",",
						scancode,
						extended?"true":"false",
						keyname_json);
					first=false;
				}
			}
		}
		fprintf(stream, "]");
	}

	//Retrieve OEM scancode mappings
	//https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-oemkeyscan
	{
		fprintf(stream, ",\"oem_mapping\":[");
		bool first=true;
		for(WORD charcode=0; charcode<256; charcode++) {
			DWORD oemmapping = OemKeyScan(charcode);
			if(oemmapping!=-1) {
				WORD scancode = LOWORD(oemmapping);
				WORD shiftstate = HIWORD(oemmapping);
				fprintf(stream,
					"%s{\"charcode\":%u,"
					"\"scancode\":%u,"
					"\"shift\":%s,"
					"\"ctrl\":%s,"
					"\"alt\":%s,"
					"\"hankaku\":%s,"
					"\"oem1\":%s,"
					"\"oem2\":%s}"
					,first?"":","
					,charcode
					,scancode
					,(shiftstate &  1)?"true":"false"
					,(shiftstate &  2)?"true":"false"
					,(shiftstate &  4)?"true":"false"
					,(shiftstate &  8)?"true":"false"
					,(shiftstate & 16)?"true":"false"
					,(shiftstate & 32)?"true":"false");
				first=false;
			}
		}
		fprintf(stream, "]");
	}

	fprintf(stream, "}\n");
	fflush(stream);
}

void printhelp() {
	fprintf(stderr,
		"\nPrint Windows keyboard events on stdout.\n\n"
		"Unless -f is provided, output will be JSON.\n\n"
		"Options:\n\n"
		" -c Consume non-injected events (prevent windows sending them to applications).\n\n"
		" -C Consume injected events (prevent windows sending them to applications).\n\n"
		" -i Also print injected events.\n\n"
		" -e Exit when escape key is pressed.\n\n"
		" -d Exit after 20 events are processed (useful for debugging).\n\n"
		" -l At startup, print a message containing information about the current\n"
		"    keyboard layout and state.\n\n"
		" -L Exit after printing startup message (implies -l).\n\n"
		" -f Output in fixed width format:\n"
		"    Column Content\n"
		"        1  'u' if key-up, 'd' if key-down\n"
		"        2  Space\n"
		"      3-6  Scan code, 4 hex digits\n"
		"        7  Space\n"
		"      8-9  Virtual key code, 2 hex digits\n"
		"       10  Space\n"
		"       11  'e' if extended, otherwise '-'\n"
		"       12  'i' if injected (from any process), otherwise '-'\n"
		"       13  'l' if injected (from process at lower integrity level),\n"
		"               otherwise '-'\n"
		"       14  'a' if alt down, otherwise '-'\n"
		"       15  Space\n"
		"    16-23  Time (ms since system start), 8 hex digits\n\n"
		" -h Print this help text and exit.\n\n"
		"listenkey is part of keyboa, pre-release\n"
		"Copyright © 2019 Axel Svensson <mail@axelsvensson.com>\n"
	);
	exit(0);
}

// The main function processes the arguments and starts runlistenkey
int main(int argc, char** argv) {
	char* progname = argv[0];
	int c;
	while ((c = getopt (argc, argv, "cCiedjflLh")) != -1) {
		switch (c) {
			case 'c': opt_c = true;  break;
			case 'C': opt_C = true;  break;
			case 'i': opt_i = true;  break;
			case 'e': opt_e = true;  break;
			case 'd': opt_d = true;  break;
			case 'f': opt_f = true;  break;
			case 'l': opt_l = true;  break;
			case 'L': opt_L = true; opt_l = true;  break;
			case 'h': printhelp();
			default: abort();
		}
	}
	if(opt_l && opt_f) {
		fprintf(stderr, "Options -l and -L are incompatible with -f.\n");
		exit(1);
	}
	signal(SIGINT, quitlistenkey);
	signal(SIGTERM, quitlistenkey);
	if(opt_l) {
		printinit(stdout);
		if(opt_L) {
			exit(0);
		}
	}
	runlistenkey(processevent, progname);
}
