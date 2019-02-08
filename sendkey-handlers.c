#include "common.h"
#include "libsendkey.h"
#include <stdio.h>

void sendkey_printjson_handler(struct keyevent *ke) {
	BOOL td = (ke->eventtype == KEYEVENT_T_KEYDOWN);
	BOOL tu = (ke->eventtype == KEYEVENT_T_KEYUP);
	BOOL tc = (ke->eventtype == KEYEVENT_T_UNICODE_CHARACTER);
	BOOL to = !(td || tu || tc);
	if(td) printf("{\"type\":\"keydown\"");
	if(tu) printf("{\"type\":\"keyup\"");
	if(tc) printf("{\"type\":\"unicode_character\"");
	if(to) printf("{\"type\":\"nothing\"");
	if((td || tu) && ke->scancode)
		printf(",\"win_scancode\":%u", ke->scancode);
	if((td || tu) && ke->virtualkey)
		printf(",\"win_virtualkey\":%u,\"win_extended\":\"%s\"",
			   ke->virtualkey,
			   ke->extended ? "true" : "false");
	if(!to && ke->altdown)
		printf(",\"win_altdown\":\"true\"");
	if((tc && ke->unicode_codepoint)
	   || ((td || tu)
		   && ke->unicode_codepoint
		   && !ke->scancode
		   && !ke->virtualkey))
		printf(",\"unicode_codepoint\":%u", ke->unicode_codepoint);
	printf("}\n");
}
