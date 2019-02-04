#include <stdio.h>

#define DWORD int
#define int_4 long int

#include <assert.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>

#include "jsonsl.c"
#include "json-str.c"

#define BOOL unsigned short
#define TRUE 1
#define FALSE 0

#define BUFFER_SIZE 10240

enum keyevent_type {
	KEYEVENT_T_UNDEFINED = 0,
	KEYEVENT_T_KEYUP = 1,
	KEYEVENT_T_KEYDOWN = 2,
	KEYEVENT_T_UNICODE_CHARACTER = 3
};

struct keyevent {
	enum keyevent_type eventtype;
	DWORD scancode;
	DWORD virtualkey;
	BOOL extended;
	BOOL altdown;
	uint32_t unicode_codepoint;
};

struct parse_context {
	//key event data
	struct keyevent keyevent;
	//parse state
	signed long min_available;
	signed long min_needed;
	void* buffer;
	size_t buffer_writeat;
	size_t buffer_len;
	BOOL need_look_back;
	size_t hkeystart;
	size_t hkeyend;
};

int error_callback(jsonsl_t jsn,
				   jsonsl_error_t err,
				   struct jsonsl_state_st *state,
				   char *at) {
	//todo maybe position isn't meaningful
	fprintf(stderr,
			"JSON parse error at position %lu: %s\n"
			"Remaining text: %s\n",
			jsn->pos,
			jsonsl_strerror(err),
			at);
	fflush(stderr);
	exit(1);
	return 0;
}

void callback(jsonsl_t jsn,
			  jsonsl_action_t action,
			  struct jsonsl_state_st *state,
			  const char *at) {
	struct parse_context *pc = (struct parse_context*)(jsn->data);
	unsigned type = state->type;
	unsigned int level = state->level;
	struct keyevent* ke = &(pc->keyevent);

	//at beginning of top-level object
	if(level == 1 && type == JSONSL_T_OBJECT && action == JSONSL_ACTION_PUSH) {
		//reset key event data
		ke->eventtype = KEYEVENT_T_UNDEFINED;
		ke->scancode=0;
		ke->virtualkey=0;
		ke->extended=FALSE;
		ke->altdown=FALSE;
		ke->unicode_codepoint=0;
	}

	//at end of top-level object
	if(level == 1 && type == JSONSL_T_OBJECT && action == JSONSL_ACTION_POP) {
		//handle keyevent
		fprintf(stderr,
			"Handle this!\n"
			"eventtype:        %u\n"
			"scancode:         %u\n"
			"virtualkey:       %u\n"
			"extended:         %u\n"
			"altdown:          %u\n"
			"unicode_codepoint %u\n\n",
			ke->eventtype,
			ke->scancode,
			ke->virtualkey,
			ke->extended,
			ke->altdown,
			ke->unicode_codepoint);
		fflush(stderr);
		jsonsl_stop(jsn);
	}

	//We're only interested in 2nd-level key/value pairs
	if(level == 2 && type == JSONSL_T_HKEY && action == JSONSL_ACTION_PUSH) {
		pc->need_look_back = TRUE;
	}
	if(level == 2 && (type == JSONSL_T_STRING || type == JSONSL_T_SPECIAL) && action == JSONSL_ACTION_POP) {
		pc->need_look_back = FALSE;
	}
	//Unless we're interested, allow discarding data
	if(!pc->need_look_back) {
		pc->min_needed = state->pos_cur;
	}

	//At end of object key
	if(level == 2 && type == JSONSL_T_HKEY && action == JSONSL_ACTION_POP) {
		//Save the position
		pc->hkeystart = state->pos_begin;
		pc->hkeyend = state->pos_cur;
	}

	//At end of value for a key
	if(level == 2 && type != JSONSL_T_HKEY && action == JSONSL_ACTION_POP) {
		//figure out which key the value was given for
		char* keyname = malloc(sizeof(char) * (pc->hkeyend - pc->hkeystart));
		if(0 <= json_string_value_to_ascii(
					pc->buffer + pc->hkeystart - pc->min_available,
					pc->buffer + pc->hkeyend - pc->min_available,
					keyname)) {
			jsonsl_type_t t = state->type;
			jsonsl_special_t f = state->special_flags;
			BOOL isstring = (t == JSONSL_T_STRING)?1:0;
			BOOL ispint = (t == JSONSL_T_SPECIAL) && (f & JSONSL_SPECIALf_UNSIGNED) && !(f & JSONSL_SPECIALf_NUMNOINT);
			uint32_t intval = state->nelem;
			BOOL isbool = (t == JSONSL_T_SPECIAL) && (f & JSONSL_SPECIALf_BOOLEAN)?1:0;
			BOOL boolval = (f & JSONSL_SPECIALf_TRUE)?1:0;

			if(strcmp(keyname, "type")==0) {
				if(isstring) {
					char* stringvalue = malloc(sizeof(char) * (state->pos_cur - state->pos_begin));
					if(0 <= json_string_value_to_ascii(
								pc->buffer + state->pos_begin - pc->min_available,
								pc->buffer + state->pos_cur - pc->min_available,
								stringvalue)) {
						if(strcmp(stringvalue, "keyup")==0) {
							ke->eventtype = KEYEVENT_T_KEYUP;
						}
						else if(strcmp(stringvalue, "keydown")==0) {
							ke->eventtype = KEYEVENT_T_KEYDOWN;
						}
						else if(strcmp(stringvalue, "unicode_character")==0) {
							ke->eventtype = KEYEVENT_T_UNICODE_CHARACTER;
						}
						else {
							fprintf(stderr, "Illegal value for %s\n", keyname);
						}
					}
					else {
						fprintf(stderr, "Illegal value for %s\n", keyname);
					}
					free(stringvalue);
				}
				else {
					fprintf(stderr, "Value for %s must be a string\n", keyname);
				}
			}
			else if(strcmp(keyname, "win_scancode")==0) {
				if(ispint) {
					ke->scancode = intval;
				}
				else {
					fprintf(stderr, "Value for %s must be a positive integer\n", keyname);
				}
			}
			else if(strcmp(keyname, "win_virtualkey")==0) {
				if(ispint) {
					ke->virtualkey = intval;
				}
				else {
					fprintf(stderr, "Value for %s must be a positive integer\n", keyname);
				}
			}
			else if(strcmp(keyname, "unicode_codepoint")==0) {
				if(ispint) {
					ke->unicode_codepoint = intval;
				}
				else {
					fprintf(stderr, "Value for %s must be a positive integer\n", keyname);
				}
			}
			else if(strcmp(keyname, "win_extended")==0) {
				if(isbool) {
					ke->extended = boolval;
				}
				else {
					fprintf(stderr, "Value for %s must be a boolean\n", keyname);
				}
			}
			else if(strcmp(keyname, "win_altdown")==0) {
				if(isbool) {
					ke->altdown = boolval;
				}
				else {
					fprintf(stderr, "Value for %s must be a boolean\n", keyname);
				}
			}
		}
		free(keyname);
	}
}

int main(int argc, char **argv) {
	struct parse_context pc={};
	jsonsl_char_t buffer[BUFFER_SIZE];
	int charsize = sizeof(jsonsl_char_t);
	pc.buffer_len = BUFFER_SIZE * (charsize);
	pc.buffer = (void*) buffer;
	pc.buffer_writeat = 0;
	jsonsl_t jsn;
	jsn = jsonsl_new(0x100);
	jsonsl_enable_all_callbacks(jsn);
	jsn->action_callback = callback;
	jsn->error_callback = error_callback;
	jsn->max_callback_level = 3;
	jsn->data = &pc;
	while(TRUE) {
		ssize_t maxread = pc.buffer_len-pc.buffer_writeat;
		if(maxread<=0) {
			fprintf(stderr, "Error: Buffer exhausted\n");
			fflush(stderr);
			exit(1);
		}
		void* buffer_process = pc.buffer + pc.buffer_writeat;
		ssize_t nread = read(0, buffer_process, maxread);
		pc.buffer_writeat += nread;
		ssize_t toprocess = nread;
		while(toprocess>=charsize) {
			int posbefore = jsn->pos;
			jsonsl_feed(jsn, (jsonsl_char_t*) buffer_process, toprocess);
			int bytesprocessed = (jsn->pos - posbefore + 1)*charsize;
			toprocess -= bytesprocessed;
			buffer_process += bytesprocessed;
			if(jsn->level == 0) {
				pc.min_available -= (jsn->pos);
				pc.min_needed=0;
				jsonsl_reset(jsn);
			}
		}
		if(pc.min_available < pc.min_needed) {
			unsigned long shift_chars = pc.min_needed - pc.min_available;
			size_t shift_bytes = shift_chars*charsize;
			memcpy(pc.buffer, pc.buffer + shift_bytes, pc.buffer_writeat - shift_bytes);
			pc.min_available += shift_chars;
			pc.buffer_writeat -= shift_bytes;
		}
		if(nread <= 0) {
			if(jsn->level == 0) {
				fprintf(stderr, "Done: End of input.\n");
				fflush(stderr);
				exit(0);
			}
			else {
				fprintf(stderr, "Error: Input ended during parsing.\n");
				fflush(stderr);
				exit(1);
			}
		}
	}
}
