// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// Legal: See COPYING.txt
#include "common.h"
#include "libsendkey.h"
#include <stdio.h>
#include <sys/stat.h>
#include "jsonsl/jsonsl.c"
#include "json-str.c"

#define BUFFER_SIZE 102400

struct parse_context {
	//key event data
	struct kmevent kmevent;
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
	char errmsg[BUFFER_SIZE + 0x100];
	sprintf(errmsg,
			"JSON parse error %s -- Remaining text: %s",
			jsonsl_strerror(err),
			at);
	global_sendkey_error_handler(true, "Cannot read input", errmsg);
	return 0;
}

void callback(jsonsl_t jsn,
			  jsonsl_action_t action,
			  struct jsonsl_state_st *state,
			  const char *at) {
	struct parse_context *pc = (struct parse_context*)(jsn->data);
	unsigned type = state->type;
	unsigned int level = state->level;
	struct kmevent* kme = &(pc->kmevent);

	//at beginning of top-level object
	if(level == 1 && type == JSONSL_T_OBJECT && action == JSONSL_ACTION_PUSH) {
		//reset key event data
#define X(f, v) kme->f = v; kme->f##_present = false;
		X(eventtype, 0)
		X(unicode_codepoint, 0)
		X(win_button, 0)
		X(win_extended, false)
		X(win_pointerx_primprim, 0)
		X(win_pointery_primprim, 0)
		X(win_pointerx_rellegacyacc, 0)
		X(win_pointery_rellegacyacc, 0)
		X(win_pointerx_virtvirt, 0)
		X(win_pointery_virtvirt, 0)
		X(win_scancode, 0)
		X(win_time, 0)
		X(win_virtualkey, 0)
		X(win_wheeldeltax, 0)
		X(win_wheeldeltay, 0)
#undef  X
	}

	//at end of top-level object
	if(level == 1 && type == JSONSL_T_OBJECT && action == JSONSL_ACTION_POP) {
		//handle kmevent
		global_sendkey_kmevent_handler(kme);
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
			bool isint = (t == JSONSL_T_SPECIAL) && !(f & JSONSL_SPECIALf_NUMNOINT) && !(f & JSONSL_SPECIALf_FLOAT) && ((f & JSONSL_SPECIALf_SIGNED) || (f & JSONSL_SPECIALf_UNSIGNED));
			bool ispint = isint && (f & JSONSL_SPECIALf_UNSIGNED);
			uint32_t intval = state->nelem;
			bool isbool = ((t == JSONSL_T_SPECIAL) && (f & JSONSL_SPECIALf_BOOLEAN));
			bool boolval = (f & JSONSL_SPECIALf_TRUE)?true:false;
			// parse type
			if(strcmp(keyname, "type")==0) {
				if(t == JSONSL_T_STRING) {
					char* stringvalue = malloc(sizeof(char) * (state->pos_cur - state->pos_begin));
					if(0 <= json_string_value_to_ascii(
								pc->buffer + state->pos_begin - pc->min_available,
								pc->buffer + state->pos_cur - pc->min_available,
								stringvalue)) {
						kme->eventtype_present = true;
						kme->eventtype = 0;
						for(int i=0; i<LEN(kmevent_type_names); i++) {
							if(kmevent_type_names[i])
								if(strcmp(stringvalue, kmevent_type_names[i])==0)
									kme->eventtype=i;
						}
						if(!kme->eventtype){
							fprintf(stderr, "Unknown event type\n");
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
			// parse unicode_codepoint
			else if(strcmp(keyname, "unicode_codepoint")==0) {
				if(ispint) {
					kme->unicode_codepoint = intval;
					kme->unicode_codepoint_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be a positive integer\n", keyname);
				}
			}
			// parse win_button
			else if(strcmp(keyname, "win_button")==0) {
				if(t == JSONSL_T_STRING) {
					char* stringvalue = malloc(sizeof(char) * (state->pos_cur - state->pos_begin));
					if(0 <= json_string_value_to_ascii(
								pc->buffer + state->pos_begin - pc->min_available,
								pc->buffer + state->pos_cur - pc->min_available,
								stringvalue)) {
						kme->win_button_present = true;
						kme->win_button = 0;
						for(int i=0; i<LEN(win_button_names); i++) {
							if(win_button_names[i])
								if(strcmp(stringvalue, win_button_names[i])==0)
									kme->win_button=i;
						}
						if(!kme->win_button){
							fprintf(stderr, "Invalid value for %s\n", keyname);
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
			// parse win_extended
			else if(strcmp(keyname, "win_extended")==0) {
				if(isbool) {
					kme->win_extended = boolval;
					kme->win_extended_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be a boolean\n", keyname);
				}
			}
			// parse win_pointerx_primprim
			else if(strcmp(keyname, "win_pointerx_primprim")==0) {
				if(isint) {
					kme->win_pointerx_primprim = intval;
					kme->win_pointerx_primprim_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be an integer\n", keyname);
				}
			}
			// parse win_pointery_primprim
			else if(strcmp(keyname, "win_pointery_primprim")==0) {
				if(isint) {
					kme->win_pointery_primprim = intval;
					kme->win_pointery_primprim_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be an integer\n", keyname);
				}
			}
			// parse win_pointerx_rellegacyacc
			else if(strcmp(keyname, "win_pointerx_rellegacyacc")==0) {
				if(isint) {
					kme->win_pointerx_rellegacyacc = intval;
					kme->win_pointerx_rellegacyacc_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be an integer\n", keyname);
				}
			}
			// parse win_pointery_rellegacyacc
			else if(strcmp(keyname, "win_pointery_rellegacyacc")==0) {
				if(isint) {
					kme->win_pointery_rellegacyacc = intval;
					kme->win_pointery_rellegacyacc_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be an integer\n", keyname);
				}
			}
			// parse win_pointerx_virtvirt
			else if(strcmp(keyname, "win_pointerx_virtvirt")==0) {
				if(isint) {
					kme->win_pointerx_virtvirt = intval;
					kme->win_pointerx_virtvirt_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be an integer\n", keyname);
				}
			}
			// parse win_pointery_virtvirt
			else if(strcmp(keyname, "win_pointery_virtvirt")==0) {
				if(isint) {
					kme->win_pointery_virtvirt = intval;
					kme->win_pointery_virtvirt_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be an integer\n", keyname);
				}
			}
			// parse win_scancode
			else if(strcmp(keyname, "win_scancode")==0) {
				if(ispint) {
					kme->win_scancode = intval;
					kme->win_scancode_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be a positive integer\n", keyname);
				}
			}
			// parse win_time
			else if(strcmp(keyname, "win_time")==0) {
				if(ispint) {
					kme->win_time = intval;
					kme->win_time_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be a positive integer\n", keyname);
				}
			}
			// parse win_virtualkey
			else if(strcmp(keyname, "win_virtualkey")==0) {
				if(ispint) {
					kme->win_virtualkey = intval;
					kme->win_virtualkey_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be a positive integer\n", keyname);
				}
			}
			// parse win_wheeldeltax
			else if(strcmp(keyname, "win_wheeldeltax")==0) {
   				if(isint) {
					kme->win_wheeldeltax = intval;
					kme->win_wheeldeltax_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be an integer\n", keyname);
				}
			}
			// parse win_wheeldeltay
			else if(strcmp(keyname, "win_wheeldeltay")==0) {
   				if(isint) {
					kme->win_wheeldeltay = intval;
					kme->win_wheeldeltay_present = true;
				}
				else {
					fprintf(stderr, "Value for %s must be an integer\n", keyname);
				}
			}
		}
		free(keyname);
	}
}

_Static_assert (sizeof(jsonsl_char_t)==1, "char size 1 is assumed");
_Static_assert (sizeof(char)==1, "char size 1 is assumed");
void sendkey_json_parser() {
	struct parse_context pc={};
	jsonsl_char_t buffer[BUFFER_SIZE+1]; //One extra for null temination
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
			global_sendkey_error_handler(true, "Cannot read input", "Buffer exhausted");
		}
		void* buffer_process = pc.buffer + pc.buffer_writeat;
		ssize_t nread = read(0, buffer_process, maxread);
		((char*)buffer_process)[nread] = 0; //add terminating null
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
				global_sendkey_error_handler(true, "Cannot read input", "Input ended during parsing");
			}
		}
	}
}
