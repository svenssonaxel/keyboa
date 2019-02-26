// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// License: See LICENSE
#include "common.h"
#include "libsendkey.h"
#include <stdio.h>
#include <sys/stat.h>
#include "jsonsl.c"
#include "json-str.c"

#define BUFFER_SIZE 102400

struct parse_context {
	//key event data
	struct keyevent keyevent;
	//parse state
	signed long min_available;
	signed long min_needed;
	void* buffer;
	size_t buffer_writeat;
	size_t buffer_len;
	bool need_look_back;
	size_t hkeystart;
	size_t hkeyend;
	bool stopped;
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
		ke->extended=false;
		ke->unicode_codepoint=0;
	}

	//at end of top-level object
	if(level == 1 && type == JSONSL_T_OBJECT && action == JSONSL_ACTION_POP) {
		//handle keyevent
		global_sendkey_keyevent_handler(ke);
		pc->stopped = true;
		jsonsl_stop(jsn);
	}

	//We're only interested in 2nd-level key/value pairs
	if(level == 2 && type == JSONSL_T_HKEY && action == JSONSL_ACTION_PUSH) {
		pc->need_look_back = true;
	}
	if(level == 2 && (type == JSONSL_T_STRING || type == JSONSL_T_SPECIAL) && action == JSONSL_ACTION_POP) {
		pc->need_look_back = false;
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
	if(
		level == 2 &&
		type != JSONSL_T_HKEY &&
		action == JSONSL_ACTION_POP &&
		!(state->type == JSONSL_T_SPECIAL &&
			state->special_flags & JSONSL_SPECIALf_NULL)
	) {
		//figure out which key the value was given for
		char* keyname = malloc(sizeof(char) * (pc->hkeyend - pc->hkeystart));
		if(0 <= json_string_value_to_ascii(
					pc->buffer + pc->hkeystart - pc->min_available,
					pc->buffer + pc->hkeyend - pc->min_available,
					keyname)) {
			jsonsl_type_t t = state->type;
			jsonsl_special_t f = state->special_flags;
			bool isstring = (t == JSONSL_T_STRING)?1:0;
			bool ispint = (t == JSONSL_T_SPECIAL) && (f & JSONSL_SPECIALf_UNSIGNED) && !(f & JSONSL_SPECIALf_NUMNOINT);
			uint32_t intval = state->nelem;
			bool isbool = (t == JSONSL_T_SPECIAL) && (f & JSONSL_SPECIALf_BOOLEAN)?1:0;
			bool boolval = (f & JSONSL_SPECIALf_TRUE)?1:0;
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
						else if(strcmp(stringvalue, "keypress")==0) {
							ke->eventtype = KEYEVENT_T_KEYPRESS;
						}
						else {
							fprintf(stderr, "Unknown keyevent type\n");
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
			else if(strcmp(keyname, "time")==0) {
				if(ispint) {
					ke->time = intval;
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
		}
		free(keyname);
	}
}

void sendkey_json_parser() {
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
	while(true) {
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

			//workaround for off-by-one bug in jsonsl_stop(jsn)
			if(pc.stopped) {
				jsn->pos++;
			}

			int bytesprocessed = (jsn->pos - posbefore)*charsize;
			toprocess -= bytesprocessed;
			buffer_process += bytesprocessed;
			if(pc.stopped) {
				pc.stopped = false;
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
			buffer_process -= shift_bytes;
		}
		if(nread <= 0) {
			if(jsn->level == 0) {
				fprintf(stderr, "Done: End of input.\n");
				exit(0);
			}
			else {
				fprintf(stderr, "Error: Input ended during parsing.\n");
				exit(1);
			}
		}
	}
}
