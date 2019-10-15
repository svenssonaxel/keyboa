// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// Legal: See COPYING.txt
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

bool opt_d, opt_w, opt_x, opt_o;

void printjson(struct kmevent *kme, FILE *stream) {
	enum kmevent_type t=kme->eventtype;
	if(!t) return;
	fprintf(stream,
	        "{\"type\":\"%s\"",
	        kmevent_type_names[kme->eventtype]);
	bool is_kev = kmevent_type_is_kev(t);
	if(is_kev && kme->unicode_codepoint_present) {
		fprintf(stream, ",\"unicode_codepoint\":%u", kme->unicode_codepoint);
	}
	if(opt_w && is_kev) {
		if(kme->win_scancode_present)
			fprintf(stream, ",\"win_scancode\":%u", kme->win_scancode);
		if(kme->win_virtualkey_present)
			fprintf(stream, ",\"win_virtualkey\":%u,\"win_extended\":%s",
				kme->win_virtualkey,
				kme->win_extended ? "true" : "false");
		if(kme->win_time_present)
			fprintf(stream, ",\"win_time\":%u", kme->win_time);
	}
	if(opt_w && (t==KMEVENT_T_BUTTONDOWN || t==KMEVENT_T_BUTTONUP)) {
		if(kme->win_button_present)
			fprintf(stream,
				",\"win_button\":%s",
				win_button_names[kme->win_button]);
	}
	if(opt_w && t==KMEVENT_T_POINTERMOVE) {
		if(kme->win_pointerx_rellegacyacc_present || kme->win_pointery_rellegacyacc_present)
			fprintf(stream,
				",\"win_pointerx_rellegacyacc\":%d,\"win_pointery_rellegacyacc\":%d",
				kme->win_pointerx_rellegacyacc, kme->win_pointery_rellegacyacc);
		else if(kme->win_pointerx_primprim_present ||
			kme->win_pointery_primprim_present)
			fprintf(stream,
				",\"win_pointerx_primprim\":%d,\"win_pointery_primprim\":%d",
				kme->win_pointerx_primprim, kme->win_pointery_primprim);
		else if(kme->win_pointerx_virtvirt_present ||
			kme->win_pointery_virtvirt_present)
			fprintf(stream,
				",\"win_pointerx_virtvirt\":%d,\"win_pointery_virtvirt\":%d",
				kme->win_pointerx_virtvirt, kme->win_pointery_virtvirt);
	}
	if(opt_w && t==KMEVENT_T_WHEEL) {
		if(kme->win_wheeldeltax_present)
			fprintf(stream,
				",\"win_wheeldeltax\":%d",
				kme->win_wheeldeltax);
		if(kme->win_wheeldeltay_present)
			fprintf(stream,
				",\"win_wheeldeltay\":%d",
				kme->win_wheeldeltay);
	}
	fprintf(stream, "}\n");
	fflush(stream);
}

void sendkey_dispatch_handler(struct kmevent *kme) {
	char* kme_error = global_sendkey_validator(kme);
	if(kme_error) {
		global_sendkey_error_handler(false, "Ignoring keyevent", kme_error);
		return;
	}
	if(opt_o) {
		printjson(kme, stdout);
	}
	if(opt_d) {
		return;
	}
	global_sendkey_sender(kme);
}

void error_handler(bool critical, char* err_effect, char* err_cause) {
	fflush(stdout);
	if(err_effect)
		fprintf(stderr,"%s", err_effect);
	if(err_effect && err_cause)
		fprintf(stderr,": ");
	if(err_cause)
		fprintf(stderr,"%s", err_cause);
	fprintf(stderr,"\n");
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
	global_sendkey_kmevent_handler = sendkey_dispatch_handler;
	global_sendkey_error_handler = error_handler;
	char* progname = argv[0];
	int c;
	while ((c = getopt (argc, argv, "wxopdh")) != -1) {
		switch (c) {
			case 'w': opt_w = true;  break;
			case 'x': opt_x = true;  break;
			case 'o': opt_o = true;  break;
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
