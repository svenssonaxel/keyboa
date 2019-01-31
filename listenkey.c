#include "liblistenkey.h"
#include <unistd.h>
#include <stdio.h>
#include <signal.h>

BOOL optc, optU, optI, optO, optE, optD, optJ, optA;
int evcount;

BOOL processevent(DWORD scancode, DWORD virtualkey, DWORD flags) {
	if(optI && (flags & LLKHF_INJECTED)) {
		return FALSE;
	}
	if(optA && (flags & LLKHF_EXTENDED) == 0 && scancode == 0x021d) {
		return optc;
	}
	if(!(optU && (flags & LLKHF_UP))) {
		if(optJ) {
			printf(
				"{\"source\":\"windows\""
				",\"extended\":%s"
				",\"injected\":%s"
				",\"altdown\":%s"
				",\"up\":%s"
				",\"scancode\":%04X"
				",\"virtualkey\":%02X"
				"}",
				(flags & LLKHF_EXTENDED) ? "true " : "false",
				(flags & LLKHF_INJECTED) ? "true " : "false",
				(flags & LLKHF_ALTDOWN ) ? "true " : "false",
				(flags & LLKHF_UP      ) ? "true " : "false",
				scancode,
				virtualkey
			);
		}
		else {
			printf("%s%s%s%s%04X%02X",
				(flags & LLKHF_EXTENDED) ? "e" : "-",
				(flags & LLKHF_INJECTED) ? "i" : "-",
				(flags & LLKHF_ALTDOWN ) ? "a" : "-",
				(flags & LLKHF_UP      ) ? "u" : "d",
				scancode,
				virtualkey
			);
		}
		if(printf("\n") == -1 && optO) {
			quitlistenkey();
		}
		fflush(stdout);
		if(optD) {
			if(++evcount>20) {
				quitlistenkey();
			}
		}
	}
	if(optE) {
		if(scancode == 1 && flags == 128) {
			quitlistenkey();
		}
	}
	return optc;
}

void printhelp() {
	printf(
		"Print Windows keyboard events on stdout.\n"
		"Options:\n"
		"-c Turn on event consuming (prevents applications to see the event).\n"
		"-U Do not print up-key events.\n"
		"-I Do not print or consume injected events.\n"
		"-A Prevent AltGr from acting like two keys.\n"
		"-O Exit when stdout closes.\n"
		"-E Exit when escape key is pressed.\n"
		"-D Exit after 20 events are processed.\n"
		"-J Output in JSON format.\n"
		"-h Print this help text and exit.\n"
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
	while ((c = getopt (argc, argv, "eiadsvcUIAOEDJh")) != -1)
		switch (c) {
			case 'c': optc = TRUE;  break;
			case 'U': optU = TRUE;  break;
			case 'I': optI = TRUE;  break;
			case 'A': optA = TRUE;  break;
			case 'O': optO = TRUE;  break;
			case 'E': optE = TRUE;  break;
			case 'D': optD = TRUE;  break;
			case 'J': optJ = TRUE;  break;
			case 'h': printhelp();
			default: abort();
		}
		signal(SIGINT, quitlistenkey);
		signal(SIGTERM, quitlistenkey);
	runlistenkey(processevent, progname);
}
