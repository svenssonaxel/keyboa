// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// Legal: See COPYING.txt
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include "common.h"
#include "json-str.c"

bool opt_w, opt_v, opt_k, opt_m, opt_b, opt_c, opt_C, opt_i, opt_e, opt_d, opt_s, opt_S;

#ifdef KEYBOA_WIN
#include "common_win.h"
#include "liblistenkey_win.h"
#endif
#include "liblistenkey.h"

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
		"{\"type\":%s,\"listen_mode\":\"windows\""
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
			printf("{\"type\":\"pointermove\",listen_mode:\"windows\",\"win_eventname\":\"WM_MOUSEMOVE\"");
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
			printf("{\"type\":\"wheel\",listen_mode:\"windows\",\"win_eventname\":\"WM_MOUSEWHEEL\"");
			iswheel = true;
			break;
		case WM_MOUSEHWHEEL:
			printf("{\"type\":\"wheel\",listen_mode:\"windows\",\"win_eventname\":\"WM_MOUSEHWHEEL\"");
			iswheel = true;
			break;
		case WM_LBUTTONDOWN:
			printf("{\"type\":\"buttondown\",listen_mode:\"windows\",\"win_eventname\":\"WM_LBUTTONDOWN\",\"win_button\":\"L\"");
			break;
		case WM_LBUTTONUP:
			printf("{\"type\":\"buttonup\",listen_mode:\"windows\",\"win_eventname\":\"WM_LBUTTONUP\",\"win_button\":\"L\"");
			break;
//		case WM_LBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",listen_mode:\"windows\",\"win_eventname\":\"WM_LBUTTONDBLCLK\",\"win_button\":\"L\"");
//			break;
		case WM_RBUTTONDOWN:
			printf("{\"type\":\"buttondown\",listen_mode:\"windows\",\"win_eventname\":\"WM_RBUTTONDOWN\",\"win_button\":\"R\"");
			break;
		case WM_RBUTTONUP:
			printf("{\"type\":\"buttonup\",listen_mode:\"windows\",\"win_eventname\":\"WM_RBUTTONUP\",\"win_button\":\"R\"");
			break;
//		case WM_MENURBUTTONUP:
//			printf("{\"type\":\"buttonup\",listen_mode:\"windows\",\"win_eventname\":\"WM_MENURBUTTONUP\",\"win_button\":\"R\",\"win_context\":\"menu\"");
//			break;
//		case WM_RBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",listen_mode:\"windows\",\"win_eventname\":\"WM_RBUTTONDBLCLK\",\"win_button\":\"R\"");
//			break;
		case WM_MBUTTONDOWN:
			printf("{\"type\":\"buttondown\",listen_mode:\"windows\",\"win_eventname\":\"WM_MBUTTONDOWN\",\"win_button\":\"M\"");
			break;
		case WM_MBUTTONUP:
			printf("{\"type\":\"buttonup\",listen_mode:\"windows\",\"win_eventname\":\"WM_MBUTTONUP\",\"win_button\":\"M\"");
			break;
//		case WM_MBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",listen_mode:\"windows\",\"win_eventname\":\"WM_MBUTTONDBLCLK\",\"win_button\":\"M\"");
//			break;
		case WM_XBUTTONDOWN:
			printf("{\"type\":\"buttondown\",listen_mode:\"windows\",\"win_eventname\":\"WM_XBUTTONDOWN\"");
			isxbutton = true;
			break;
		case WM_XBUTTONUP:
			printf("{\"type\":\"buttonup\",listen_mode:\"windows\",\"win_eventname\":\"WM_XBUTTONUP\"");
			isxbutton = true;
			break;
//		case WM_XBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",listen_mode:\"windows\",\"win_eventname\":\"WM_XBUTTONDBLCLK\"");
//			isxbutton = true;
//			break;
//		case WM_NCLBUTTONDOWN:
//			printf("{\"type\":\"buttondown\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCLBUTTONDOWN\",\"win_button\":\"L\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCLBUTTONUP:
//			printf("{\"type\":\"buttonup\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCLBUTTONUP\",\"win_button\":\"L\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCLBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCLBUTTONDBLCLK\",\"win_button\":\"L\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCRBUTTONDOWN:
//			printf("{\"type\":\"buttondown\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCRBUTTONDOWN\",\"win_button\":\"R\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCRBUTTONUP:
//			printf("{\"type\":\"buttonup\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCRBUTTONUP\",\"win_button\":\"R\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCRBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCRBUTTONDBLCLK\",\"win_button\":\"R\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCMBUTTONDOWN:
//			printf("{\"type\":\"buttondown\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCMBUTTONDOWN\",\"win_button\":\"M\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCMBUTTONUP:
//			printf("{\"type\":\"buttonup\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCMBUTTONUP\",\"win_button\":\"M\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCMBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCMBUTTONDBLCLK\",\"win_button\":\"M\",\"win_context\":\"NC\"");
//			break;
//		case WM_NCXBUTTONDOWN:
//			printf("{\"type\":\"buttondown\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCXBUTTONDOWN\",\"win_context\":\"NC\"");
//			isxbutton = true;
//			break;
//		case WM_NCXBUTTONUP:
//			printf("{\"type\":\"buttonup\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCXBUTTONUP\",\"win_context\":\"NC\"");
//			isxbutton = true;
//			break;
//		case WM_NCXBUTTONDBLCLK:
//			printf("{\"type\":\"buttondoubleclick\",listen_mode:\"windows\",\"win_eventname\":\"WM_NCXBUTTONDBLCLK\",\"win_context\":\"NC\"");
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
#endif

void printinit(FILE* stream) {
	fprintf(stream, "{\"type\":\"init\",\"listen_modes\":[");
	if(opt_w)
		fprintf(stream, "\"windows\"");
	if(opt_w && opt_v)
		fprintf(stream, ",");
	if(opt_v)
		fprintf(stream, "\"x11vnc\"");
	fprintf(stream, "]}\n");
	fflush(stream);
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
	while ((c = getopt (argc, argv, "wvkmbcCiedsSh")) != -1) {
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

#ifndef KEYBOA_WIN
	if(opt_w) {
		printf("This version of listenkey is compiled without Windows API support.\n");
		exit(1);
	}
#endif
	if(opt_s) {
		printinit(stdout);
		if(opt_S) {
			exit(0);
		}
	}
	signal(SIGINT, quitlistenkey);
	signal(SIGTERM, quitlistenkey);
#ifdef KEYBOA_WIN
	if(opt_w) {
		runlistenkey(
			// Listen to key events if we need to print them or exit on Esc.
			(opt_k || opt_e) ? processKeyEvent : NULL,
			// Listen to mouse events if we need to print move or button events.
			(opt_m || opt_b) ? processMouseEvent : NULL,
			progname);
	}
#endif
	if(opt_v) {
		printf("x11vnc support not yet implemented.\n");
		exit(1);
	}
}
