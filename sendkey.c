// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// License: See LICENSE
#include <unistd.h>
#include <stdio.h>
#include <signal.h>
#include "common.h"
#include "libsendkey.h"
#include "sendkey-json-parser.c"

bool opt_d, opt_o, opt_p, opt_t;

void printjson(struct keyevent *ke, FILE *stream) {
	bool td = (ke->eventtype == KEYEVENT_T_KEYDOWN);
	bool tu = (ke->eventtype == KEYEVENT_T_KEYUP);
	bool tp = (ke->eventtype == KEYEVENT_T_KEYPRESS);
	bool to = !(td || tu || tp);
	if(td) fprintf(stream, "{\"type\":\"keydown\"");
	if(tu) fprintf(stream, "{\"type\":\"keyup\"");
	if(tp) fprintf(stream, "{\"type\":\"keypress\"");
	if(to) fprintf(stream, "{\"type\":\"nothing\"");
	if(ke->scancode)
		fprintf(stream, ",\"win_scancode\":%u", ke->scancode);
	if(ke->virtualkey)
		fprintf(stream, ",\"win_virtualkey\":%u,\"win_extended\":%s",
			   ke->virtualkey,
			   ke->extended ? "true" : "false");
	if(ke->time) {
		fprintf(stream, ",\"win_time\":%u", ke->time);
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
	if(ke->scancode)
		fprintf(stream, ",\n \"win_scancode\":      %5u", ke->scancode);
	if(ke->virtualkey)
		fprintf(stream, ",\n \"win_virtualkey\":    %5u,\n \"win_extended\":       %s",
			   ke->virtualkey,
			   ke->extended ? "true" : "false");
	if(ke->time) {
		fprintf(stream, ",\n \"win_time\": %u", ke->time);
	}
	if(ke->unicode_codepoint) {
		fprintf(stream, ",\n \"unicode_codepoint\": %u", ke->unicode_codepoint);
	}
	fprintf(stream, "}\n\n");
	fflush(stream);
}

void sendkey_dispatch_handler(struct keyevent *ke) {
	char* ke_error = validate_keyevent(ke);
	if(ke_error) {
		global_sendkey_error_handler(false, "Ignoring keyevent", ke_error);
	}
	else {
		if(!opt_d) {
			send_keyevent(ke);
		}
		if(opt_p) {
			printprettyjson(ke, stdout);
		}
		else if(opt_o) {
			printjson(ke, stdout);
		}
	}
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
		"\nInject Windows keyboard events read from stdin.\n\n"
		"Options:\n\n"
		" -d Dry run: Do not inject events.\n"
		" -o Also print events on stdout.\n"
		" -p Pretty-print on stdout (implies -o).\n"
		" -t Where win_time is not provided, use current time yet always increase it.\n"
		" -h Print this help text and exit.\n\n"
		"sendkey is part of keyboa, pre-release\n"
		"Copyright © 2019 Axel Svensson <mail@axelsvensson.com>\n"
	);
	exit(0);
}

int main(int argc, char* argv[]) {
	global_sendkey_keyevent_handler = sendkey_dispatch_handler;
	global_sendkey_error_handler = error_handler;
	char* progname = argv[0];
	int c;
	while ((c = getopt (argc, argv, "dopth")) != -1) {
		switch (c) {
			case 'd': opt_d = true;  break;
			case 'o': opt_o = true;  break;
			case 'p': opt_p = true;  break;
			case 't': opt_t = true;  break;
			case 'h': printhelp();
			default: abort();
		}
	}
	signal(SIGINT, quitsignal);
	signal(SIGTERM, quitsignal);
	sendkey_json_parser(opt_t);
}
