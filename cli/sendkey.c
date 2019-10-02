// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// License: See LICENSE
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include "common.h"
#include "libsendkey.h"
#include "sendkey-json-parser.c"
#include "version.h"

#ifdef keyboa_win
#include "common_win.h"
#include "libsendkey_win.h"
#endif

bool opt_d, opt_w, opt_x, opt_o, opt_p;

void printjson(struct keyevent *ke, FILE *stream) {
	bool td = (ke->eventtype == KEYEVENT_T_KEYDOWN);
	bool tu = (ke->eventtype == KEYEVENT_T_KEYUP);
	bool tp = (ke->eventtype == KEYEVENT_T_KEYPRESS);
	bool to = !(td || tu || tp);
	if(td) fprintf(stream, "{\"type\":\"keydown\"");
	if(tu) fprintf(stream, "{\"type\":\"keyup\"");
	if(tp) fprintf(stream, "{\"type\":\"keypress\"");
	if(to) fprintf(stream, "{\"type\":\"nothing\"");
	if(opt_w) {
		if(ke->win_scancode)
			fprintf(stream, ",\"win_scancode\":%u", ke->win_scancode);
		if(ke->win_virtualkey)
			fprintf(stream, ",\"win_virtualkey\":%u,\"win_extended\":%s",
				ke->win_virtualkey,
				ke->win_extended ? "true" : "false");
		if(ke->win_time)
			fprintf(stream, ",\"win_time\":%u", ke->win_time);
	}
	if(ke->unicode_codepoint) {
		fprintf(stream, ",\"unicode_codepoint\":%u", ke->unicode_codepoint);
	}
	fprintf(stream, "}\n");
	fflush(stream);
}

void printprettyjson(struct keyevent *ke, FILE *stream) {
	bool td = (ke->eventtype == KEYEVENT_T_KEYDOWN);
	bool tu = (ke->eventtype == KEYEVENT_T_KEYUP);
	bool tp = (ke->eventtype == KEYEVENT_T_KEYPRESS);
	bool to = !(td || tu || tp);
	fprintf(stream, "{\"type\":         ");
	if(td) fprintf(stream, " \"keydown\"");
	if(tu) fprintf(stream, "   \"keyup\"");
	if(tp) fprintf(stream, "\"keypress\"");
	if(to) fprintf(stream, " \"nothing\"");
	if(opt_w) {
		if(ke->win_scancode_present)
			fprintf(stream, ",\n \"win_scancode\":      %5u", ke->win_scancode);
		if(ke->win_virtualkey_present)
			fprintf(stream, ",\n \"win_virtualkey\":    %5u,\n \"win_extended\":       %s",
				ke->win_virtualkey,
				ke->win_extended ? "true" : "false");
		if(ke->win_time_present)
			fprintf(stream, ",\n \"win_time\": %u", ke->win_time);
	}
	if(ke->unicode_codepoint_present) {
		fprintf(stream, ",\n \"unicode_codepoint\": %u", ke->unicode_codepoint);
	}
	fprintf(stream, "}\n\n");
	fflush(stream);
}

void sendkey_dispatch_handler(struct keyevent *ke) {
	char* ke_error = global_sendkey_validator(ke);
	if(ke_error) {
		global_sendkey_error_handler(false, "Ignoring keyevent", ke_error);
		return;
	}
	if(opt_p) {
		printprettyjson(ke, stdout);
	}
	else if(opt_o) {
		printjson(ke, stdout);
	}
	if(opt_d) {
		return;
	}
	global_sendkey_sender(ke);
}

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

void quitsignal() {
	fprintf(stderr, "Quitting due to signal.\n");
	fflush(stderr);
	exit(0);
}

void printhelp() {
	fprintf(stderr,
		"\nInject user input events read from stdin.\n\n"
		"Options:\n\n"
		" -w Windows mode: Inject using Windows API.\n"
		" -x X11 mode: Inject into X11 session.\n"
		" -o Also print events on stdout.\n"
		" -p Pretty-print on stdout (implies -o).\n"
		" -d Dry run: Do not inject events.\n"
		" -h Print this help text and exit.\n"
		"\nFor more help: man sendkey\n\n"
		"sendkey is part of keyboa version %s\n"
		"Copyright © 2019 Axel Svensson <mail@axelsvensson.com>\n"
		,KEYBOAVERSION
	);
	exit(0);
}

int main(int argc, char* argv[]) {
	global_sendkey_keyevent_handler = sendkey_dispatch_handler;
	global_sendkey_error_handler = error_handler;
	char* progname = argv[0];
	int c;
	while ((c = getopt (argc, argv, "wxopdh")) != -1) {
		switch (c) {
			case 'w': opt_w = true;  break;
			case 'x': opt_x = true;  break;
			case 'o': opt_o = true;  break;
			case 'p': opt_p = true;  break;
			case 'd': opt_d = true;  break;
			case 'h': printhelp();
			default: abort();
		}
	}
	if(((opt_w?1:0)+(opt_x?1:0))>1) {
		printf("Only one of -wx can be given.\n");
		exit(1);
	}
	if(!(opt_w||opt_x)) {
#ifdef keyboa_win
		opt_w = true;
#else
		opt_x = true;
#endif
	}
	if(opt_w) {
#ifdef keyboa_win
		sendkey_init_win();
#else
		printf("This version of sendkey is compiled without Windows API support.\n");
		exit(1);
#endif
	}
	if(opt_x) {
		printf("X11 support not yet implemented.\n");
		exit(1);
	}
	signal(SIGINT, quitsignal);
	signal(SIGTERM, quitsignal);
	sendkey_json_parser();
}
