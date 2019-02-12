#include "common.h"
#include "libsendkey.h"
#include <stdio.h>

void sendkey_printjson_handler(struct keyevent *ke) {
	bool td = (ke->eventtype == KEYEVENT_T_KEYDOWN);
	bool tu = (ke->eventtype == KEYEVENT_T_KEYUP);
	bool tc = (ke->eventtype == KEYEVENT_T_UNICODE_CHARACTER);
	bool to = !(td || tu || tc);
	if(td) printf("{\"type\":\"keydown\"");
	if(tu) printf("{\"type\":\"keyup\"");
	if(tc) printf("{\"type\":\"unicode_character\"");
	if(to) printf("{\"type\":\"nothing\"");
	if((td || tu) && ke->scancode)
		printf(",\"win_scancode\":%u", ke->scancode);
	if((td || tu) && ke->virtualkey)
		printf(",\"win_virtualkey\":%u,\"win_extended\":%s",
			   ke->virtualkey,
			   ke->extended ? "true" : "false");
	if(!to && ke->altdown)
		printf(",\"win_altdown\":true");
	if((tc && ke->unicode_codepoint)
	   || ((td || tu)
		   && ke->unicode_codepoint
		   && !ke->scancode
		   && !ke->virtualkey))
		printf(",\"unicode_codepoint\":%u", ke->unicode_codepoint);
	printf("}\n");
	fflush(stdin);
}

void sendkey_printprettyjson_handler(struct keyevent *ke) {
	bool td = (ke->eventtype == KEYEVENT_T_KEYDOWN);
	bool tu = (ke->eventtype == KEYEVENT_T_KEYUP);
	bool tc = (ke->eventtype == KEYEVENT_T_UNICODE_CHARACTER);
	bool to = !(td || tu || tc);
	printf("{\"type\":              ");
	if(td) printf("\"keydown\"");
	if(tu) printf("\"keyup\"");
	if(tc) printf("\"unicode_character\"");
	if(to) printf("\"nothing\"");
	if((td || tu) && ke->scancode)
		printf(",\n \"win_scancode\":      %5u", ke->scancode);
	if((td || tu) && ke->virtualkey)
		printf(",\n \"win_virtualkey\":    %5u,\n \"win_extended\":      %s",
			   ke->virtualkey,
			   ke->extended ? "true" : "false");
	if(!to && ke->altdown)
		printf(",\n \"win_altdown\":       true");
	if((tc && ke->unicode_codepoint)
	   || ((td || tu)
		   && ke->unicode_codepoint
		   && !ke->scancode
		   && !ke->virtualkey))
		printf(",\n \"unicode_codepoint\": %u", ke->unicode_codepoint);
	printf("}\n\n");
	fflush(stdin);
}
