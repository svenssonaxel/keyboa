#include "liblistenkey.h"
#include <unistd.h>
#include <stdio.h>
#include <signal.h>

BOOL opt_c, opt_i, opt_e, opt_d, opt_f;
int evcount;

BOOL processevent(DWORD scancode, DWORD virtualkey, DWORD flags) {
	if(opt_i && (flags & LLKHF_INJECTED)) {
		return FALSE;
	}
	if(!opt_f) {
		printf(
			"{\"win_scancode\":%5u"
			",\"win_virtualkey\":%3u"
			",\"win_extended\":%s"
			",\"win_injected\":%s"
			",\"win_lower_il_injected\":%s"
			",\"win_altdown\":%s"
			",\"type\":%s}",
			scancode,
			virtualkey,
			(flags & LLKHF_EXTENDED) ? "true " : "false",
			(flags & LLKHF_INJECTED) ? "true " : "false",
			(flags & LLKHF_LOWER_IL_INJECTED) ? "true " : "false",
			(flags & LLKHF_ALTDOWN) ? "true " : "false",
			(flags & LLKHF_UP) ? "\"keyup\"  " : "\"keydown\""
		);
	}
	if(opt_f) {
		printf("%04x %02x %s%s%s%s%s",
			scancode,
			virtualkey,
			(flags & LLKHF_EXTENDED) ? "e" : "-",
			(flags & LLKHF_INJECTED) ? "i" : "-",
			(flags & LLKHF_LOWER_IL_INJECTED) ? "l" : "-",
			(flags & LLKHF_ALTDOWN) ? "a" : "-",
			(flags & LLKHF_UP) ? "u" : "d"
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
	return opt_c;
}

void printhelp() {
	fprintf(stderr,
		"\nPrint Windows keyboard events on stdout.\n\n"
		"Unless -f is provided, output will be JSON.\n\n"
		"Options:\n\n"
		" -c Consume events (prevent windows sending them to applications).\n\n"
		" -i Do not print injected events.\n"
		"    Also, do not consume injected events even if -c is present.\n\n"
		" -e Exit when escape key is pressed.\n\n"
		" -d Exit after 20 events are processed (useful for debugging).\n\n"
		" -f Output in fixed width format:\n"
		"    Column Content\n"
		"      1-4  Scan code, 4 hex digits\n"
		"        5  Space\n"
		"      6-7  Virtual key code, 2 hex digits\n"
		"        8  Space\n"
		"        9  'e' if extended, otherwise '-'\n"
		"       10  'i' if injected (from any process), otherwise '-'\n"
		"       11  'l' if injected (from process at lower integrity level),\n"
		"               otherwise '-'\n"
		"       12  'a' if alt down, otherwise '-'\n"
		"       13  'u' if key-up, 'd' if key-down\n\n"
		" -h Print this help text and exit.\n\n"
	);
	exit(0);
}

// The main function processes the arguments and starts runlistenkey
int main(int argc, char** argv) {
	if(argc == 1) {
		printhelp();
	}
	char* progname = argv[0];
	int c;
	while ((c = getopt (argc, argv, "ciedjfh")) != -1) {
		switch (c) {
			case 'c': opt_c = TRUE;  break;
			case 'i': opt_i = TRUE;  break;
			case 'e': opt_e = TRUE;  break;
			case 'd': opt_d = TRUE;  break;
			case 'f': opt_f = TRUE;  break;
			case 'h': printhelp();
			default: abort();
		}
	}
	signal(SIGINT, quitlistenkey);
	signal(SIGTERM, quitlistenkey);
	runlistenkey(processevent, progname);
}
