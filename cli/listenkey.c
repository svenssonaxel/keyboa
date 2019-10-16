// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// Legal: See COPYING.txt
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include "common.h"
#include "liblistenkey.h"
#include "json-str.c"

#ifdef KEYBOA_WIN
#include "common_win.h"
#include "liblistenkey_win.h"
#endif

bool opt_w, opt_v, opt_k, opt_m, opt_b, opt_c, opt_C, opt_i, opt_e, opt_d, opt_s, opt_S;
int evcount;

void error_handler(bool critical, char* errclass, char* errmsg) {
	fflush(stdout);
	fprintf(
		stderr,
		"%s: %s\n",
		errclass ? errclass : "",
		errmsg ? errmsg : "");
	if(critical) {
		fprintf(stderr, "Exiting due to critical error.\n");
		exit(1);
	}
	fflush(stderr);
}

#ifdef KEYBOA_WIN
bool processKeyEvent(WPARAM wParam, KBDLLHOOKSTRUCT* hooked) {
	DWORD     virtualkey = hooked->vkCode;
	DWORD     scancode = hooked->scanCode;
	DWORD     flags = hooked->flags;
	DWORD     time = hooked->time;
	if(opt_e) {
		if(scancode == 1 && flags == 128) {
			quitlistenkey();
			return false;
		}
	}
	if(!opt_k) {
		return false;
	}
	bool isinjected = !!(flags & LLKHF_INJECTED);
	bool consume = isinjected ? opt_C : opt_c;
	if(!opt_i && isinjected) {
		return consume;
	}
	char* lleventname="";
	char errmsg[0x100];
	switch(wParam) {
		case WM_KEYDOWN:
			lleventname="WM_KEYDOWN";
			break;
		case WM_KEYUP:
			lleventname="WM_KEYUP";
			break;
		case WM_SYSKEYDOWN:
			lleventname="WM_SYSKEYDOWN";
			break;
		case WM_SYSKEYUP:
			lleventname="WM_SYSKEYUP";
			break;
		default:
			sprintf(errmsg, "Unknown message type %d", wParam);
			error_handler(false, "Ignoring keyevent message", errmsg);
			return false;
	}
	printf(
		"{\"type\":%s"
		",\"win_scancode\":%5u"
		",\"win_virtualkey\":%3u"
		",\"win_extended\":%s"
		",\"win_injected\":%s"
		",\"win_lower_il_injected\":%s"
		",\"win_altdown\":%s"
		",\"win_time\":%10u"
		",\"win_eventname\":\"%s\"}"
		,(flags & LLKHF_UP) ? "\"keyup\"  " : "\"keydown\""
		,scancode
		,virtualkey
		,(flags & LLKHF_EXTENDED) ? "true " : "false"
		,isinjected ? "true " : "false"
		,(flags & LLKHF_LOWER_IL_INJECTED) ? "true " : "false"
		,(flags & LLKHF_ALTDOWN) ? "true " : "false"
		,time
		,lleventname
	);
	if(printf("\n") == -1) {
		quitlistenkey();
	}
	fflush(stdout);
	if(opt_d) {
		if(++evcount>20) {
			quitlistenkey();
		}
	}
	return consume;
}

bool processMouseEvent(WPARAM wParam, MSLLHOOKSTRUCT* hooked) {
	POINT     pt = hooked->pt;
	DWORD     mouseData = hooked->mouseData;
	DWORD     flags = hooked->flags;
	DWORD     time = hooked->time;
	if(!(wParam==WM_MOUSEMOVE ? opt_m : opt_b)) {
		return false;
	}
	bool isinjected = !!(flags & LLMHF_INJECTED);
	bool consume = isinjected ? opt_C : opt_c;
	if(!opt_i && isinjected) {
		return consume;
	}
	bool iswheel = false;
	bool isxbutton = false;
	char errmsg[0x100];
	switch(wParam) {
		case WM_MOUSEMOVE:
			printf("{\"type\":\"pointermove\",\"win_eventname\":\"WM_MOUSEMOVE\"");
			// Coordinates are present in all event types, but are assumed to
			// change only in WM_MOUSEMOVE.
			printf(
				",\"win_pointerx_primpixel\":%5d"
				",\"win_pointery_primpixel\":%5d"
				,pt.x
				,pt.y
			);
			break;
		case WM_MOUSEWHEEL:
			printf("{\"type\":\"wheel\",\"win_eventname\":\"WM_MOUSEWHEEL\"");
			iswheel = true;
			break;
		case WM_MOUSEHWHEEL:
			printf("{\"type\":\"wheel\",\"win_eventname\":\"WM_MOUSEHWHEEL\"");
			iswheel = true;
			break;
		case WM_LBUTTONDOWN:
			printf("{\"type\":\"buttondown\",\"win_eventname\":\"WM_LBUTTONDOWN\",\"win_button\":\"L\"");
			break;
		case WM_LBUTTONUP:
			printf("{\"type\":\"buttonup\",\"win_eventname\":\"WM_LBUTTONUP\",\"win_button\":\"L\"");
			break;
//		case WM_LBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",\"win_eventname\":\"WM_LBUTTONDBLCLK\",\"win_button\":\"L\"");
//			break;
		case WM_RBUTTONDOWN:
			printf("{\"type\":\"buttondown\",\"win_eventname\":\"WM_RBUTTONDOWN\",\"win_button\":\"R\"");
			break;
		case WM_RBUTTONUP:
			printf("{\"type\":\"buttonup\",\"win_eventname\":\"WM_RBUTTONUP\",\"win_button\":\"R\"");
			break;
//		case WM_MENURBUTTONUP:
//			printf("{\"type\":\"buttonup\",\"win_eventname\":\"WM_MENURBUTTONUP\",\"win_button\":\"R\",\"win_context\":\"menu\"");
//			break;
//		case WM_RBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",\"win_eventname\":\"WM_RBUTTONDBLCLK\",\"win_button\":\"R\"");
//			break;
		case WM_MBUTTONDOWN:
			printf("{\"type\":\"buttondown\",\"win_eventname\":\"WM_MBUTTONDOWN\",\"win_button\":\"M\"");
			break;
		case WM_MBUTTONUP:
			printf("{\"type\":\"buttonup\",\"win_eventname\":\"WM_MBUTTONUP\",\"win_button\":\"M\"");
			break;
//		case WM_MBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",\"win_eventname\":\"WM_MBUTTONDBLCLK\",\"win_button\":\"M\"");
//			break;
		case WM_XBUTTONDOWN:
			printf("{\"type\":\"buttondown\",\"win_eventname\":\"WM_XBUTTONDOWN\"");
			isxbutton = true;
			break;
		case WM_XBUTTONUP:
			printf("{\"type\":\"buttonup\",\"win_eventname\":\"WM_XBUTTONUP\"");
			isxbutton = true;
			break;
//		case WM_XBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",\"win_eventname\":\"WM_XBUTTONDBLCLK\"");
//			isxbutton = true;
//			break;
//		case WM_NCLBUTTONDOWN:
//			printf("{\"type\":\"buttondown\",\"win_eventname\":\"WM_NCLBUTTONDOWN\",\"win_button\":\"L\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCLBUTTONUP:
//			printf("{\"type\":\"buttonup\",\"win_eventname\":\"WM_NCLBUTTONUP\",\"win_button\":\"L\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCLBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",\"win_eventname\":\"WM_NCLBUTTONDBLCLK\",\"win_button\":\"L\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCRBUTTONDOWN:
//			printf("{\"type\":\"buttondown\",\"win_eventname\":\"WM_NCRBUTTONDOWN\",\"win_button\":\"R\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCRBUTTONUP:
//			printf("{\"type\":\"buttonup\",\"win_eventname\":\"WM_NCRBUTTONUP\",\"win_button\":\"R\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCRBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",\"win_eventname\":\"WM_NCRBUTTONDBLCLK\",\"win_button\":\"R\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCMBUTTONDOWN:
//			printf("{\"type\":\"buttondown\",\"win_eventname\":\"WM_NCMBUTTONDOWN\",\"win_button\":\"M\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCMBUTTONUP:
//			printf("{\"type\":\"buttonup\",\"win_eventname\":\"WM_NCMBUTTONUP\",\"win_button\":\"M\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCMBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",\"win_eventname\":\"WM_NCMBUTTONDBLCLK\",\"win_button\":\"M\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCXBUTTONDOWN:
//			printf("{\"type\":\"buttondown\",\"win_eventname\":\"WM_NCXBUTTONDOWN\",\"win_context\":\"NC\"");
//			isxbutton = true;
//			break;
//		case WM_NCXBUTTONUP:
//			printf("{\"type\":\"buttonup\",\"win_eventname\":\"WM_NCXBUTTONUP\",\"win_context\":\"NC\"");
//			isxbutton = true;
//			break;
//		case WM_NCXBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",\"win_eventname\":\"WM_NCXBUTTONDBLCLK\",\"win_context\":\"NC\"");
//			isxbutton = true;
//			break;
		default:
			sprintf(errmsg, "Unknown message type %d", wParam);
			error_handler(false, "Ignoring mouseevent message", errmsg);
			return false;
	}
	if(iswheel) {
		signed short wheelDelta = HIWORD(mouseData);
		printf(",\"win_wheeldelta%s\":%5d"
			, (wParam == WM_MOUSEHWHEEL) ? "x" : "y"
			, wheelDelta);
	}
	if(isxbutton) {
		char errmsg[0x100];
		switch(HIWORD(mouseData)) {
			case 1:
				printf(",\"win_button\":\"X1\"");
				break;
			case 2:
				printf(",\"win_button\":\"X2\"");
				break;
			default:
				sprintf(errmsg, "Unknown X button %d", HIWORD(mouseData));
				error_handler(false, "Using null for win_button", errmsg);
				printf(",\"win_button\":null");
				break;
		}
	}
	printf(
		",\"win_injected\":%s"
		",\"win_lower_il_injected\":%s"
		",\"win_time\":%10u}"
		,isinjected ? "true " : "false"
		,(flags & LLMHF_LOWER_IL_INJECTED) ? "true " : "false"
		,time
	);
	if(printf("\n") == -1) {
		quitlistenkey();
	}
	fflush(stdout);
	if(opt_d) {
		if(++evcount>20) {
			quitlistenkey();
		}
	}
	return consume;
}

void printinit_win(FILE* stream) {
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
		char errmsg[0x800];
		for(int extended=0; extended<2; extended++) {
			for(int scancode=0; scancode<256; scancode++) {
				namelen = GetKeyNameTextA(
					(scancode << 16) |
					(extended << 24),
					keyname,
					1000);
				if(namelen) {
					if(!latin1_string_to_json(keyname, keyname_json)){
						sprintf(errmsg, "Couldn't JSON-encode %s", keyname);
						error_handler(false, "latin1_string_to_json failed", errmsg);
					}
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
#endif

void printinit_x(FILE* stream) {
	fprintf(stream, "X11 support not yet implemented.\n");
	exit(1);
}

void quitsignal() {
	fprintf(stderr, "Quitting due to signal.\n");
	fflush(stderr);
	exit(0);
}

void printhelp() {
	fprintf(stderr,
		"\nPrint user input events on stdout, optionally consuming them.\n"
		"\nOptions:\n\n"
		" -w Windows mode: Receive events through Windows API.\n"
		" -v VNC mode: Receive events through an x11vnc proxy.\n"
		" -k Print keyboard events (on by default unless -m or -b is provided).\n"
		" -m Print mouse move events.\n"
		" -b Print mouse button and wheel events.\n"
		" -c Consume non-injected events.\n"
		" -C Consume injected events.\n"
		" -i Print injected events.\n"
		" -e Exit when escape key is pressed.\n"
		" -d Exit after 20 events are processed (useful for debugging).\n"
		" -s At startup, print a message containing information about the current\n"
		"    keyboard layout and state.\n"
		" -S Exit after printing startup message (implies -s).\n"
		" -h Print this help text and exit.\n"
		"\nFor more help: man listenkey\n\n"
		"listenkey is part of keyboa version %s\n"
		"Copyright © 2019 Axel Svensson <mail@axelsvensson.com>\n"
		,KEYBOAVERSION
	);
	exit(0);
}

// The main function processes the arguments and starts runlistenkey
int main(int argc, char** argv) {
	char* progname = argv[0];
	int c;
	while ((c = getopt (argc, argv, "wvkmbcCiedjfsSh")) != -1) {
		switch (c) {
			case 'w': opt_w = true;  break;
			case 'v': opt_v = true;  break;
			case 'k': opt_k = true;  break;
			case 'm': opt_m = true;  break;
			case 'b': opt_b = true;  break;
			case 'c': opt_c = true;  break;
			case 'C': opt_C = true;  break;
			case 'i': opt_i = true;  break;
			case 'e': opt_e = true;  break;
			case 'd': opt_d = true;  break;
			case 's': opt_s = true;  break;
			case 'S': opt_S = true; opt_s = true;  break;
			case 'h': printhelp();
			default: abort();
		}
	}
	// -k is on by default unless -m or -b is provided.
	if(!(opt_m || opt_b)) { opt_k = true; }
	if(((opt_w?1:0)+(opt_v?1:0))>1) {
		printf("Only one of -wv can be given.\n");
		exit(1);
	}
	if(!(opt_w||opt_v)) {
#ifdef KEYBOA_WIN
		opt_w = true;
#else
		opt_v = true;
#endif
	}

#ifdef KEYBOA_WIN
	if(opt_s) {
		if(opt_w)
			printinit_win(stdout);
		if(opt_v)
			printinit_x(stdout);
		if(opt_S) {
			exit(0);
		}
	}
	if(opt_w) {
		signal(SIGINT, quitlistenkey);
		signal(SIGTERM, quitlistenkey);
		runlistenkey(
			// Listen to key events if we need to print them or exit on Esc.
			(opt_k || opt_e) ? processKeyEvent : NULL,
			// Listen to mouse events if we need to print move or button events.
			(opt_m || opt_b) ? processMouseEvent : NULL,
			progname);
	}
	else {
		signal(SIGINT, quitsignal);
		signal(SIGTERM, quitsignal);
	}
#else
	if(opt_w) {
		printf("This version of listenkey is compiled without Windows API support.\n");
		exit(1);
	}
	else {
		if(opt_s) {
			if(opt_v)
				printinit_x(stdout);
			if(opt_S) {
				exit(0);
			}
		}
		signal(SIGINT, quitsignal);
		signal(SIGTERM, quitsignal);
	}
#endif
	if(opt_v) {
		printf("x11vnc support not yet implemented.\n");
		exit(1);
	}
}
