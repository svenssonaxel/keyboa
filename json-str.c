// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
#include "common.h"

/**
 * Converts a JSON string value to a null-terminated ASCII string.
 * This can be used with object keys as well, since the syntax is the same.
 *
 * @param beginquote Pointer to the the quote character that marks the
 * beginning of the string value
 * @param endquote Pointer to the the quote character that marks the end of the
 * string value
 * @param target A buffer able to hold the converted ASCII string. It is safe
 * to assume that the ASCII string will never be longer than the JSON string
 * value.
 * 
 * @return The number of converted characters if the conversion was successful.
 * A negative number if any part of the JSON string is illegally encoded or
 * encodes a null or non-ASCII character. ASCII characters encoded as \u00XX
 * are supported, but not encoded as an overlong surrogate pair.
 */
int json_string_value_to_ascii(char* beginquote, char* endquote, char* target) {
  if(*beginquote != '\"' || *endquote != '\"' || (endquote - beginquote) < 1) {
	return -1;
  }
  char* s = beginquote + 1;
  char* t = target;
  while(s < endquote) {
	char c = *s;
	if(c <= 0 || c == '\"' || 128 <= c) {
	  return -1;
	}
	if(c != '\\') {
	  *t = c;
	  s++;
	  t++;
	  continue;
	}
	if(endquote <= s + 1) {
	  return -1;
	}
	for(int i=0;i<8;i++) {
	  if(s[1] == "\"\\/bfnrt"[i]) {
		*t = "\"\\/\b\f\n\r\t"[i];
		s+=2;
		t++;
		break;
		continue;
	  }
	}
	if(s[1] != 'u' || endquote <= s + 5) {
	  return -1;
	}
	int code=0;
	for(int i=2;i<6;i++) {
	  code<<=4;
	  if('0' <= s[i] && s[i] <= '9') {
		code += s[i] - '0';
	  }
	  else if('A' <= s[i] && s[i] <= 'F') {
		code += s[i] - 'A' + 10;
	  }
	  else if('a' <= s[i] && s[i] <= 'f') {
		code += s[i] - 'A' + 10;
	  }
	  else {
		return -1;
	  }
	}
	if(code <= 0 || 128 <= code) {
	  return -1;
	}
	*t = code;
	s+=6;
	t++;
	continue;
  }
  *t = 0;
  return t - target;
}

/**
 * Converts a null-terminated Latin-1 encoded string to a null-terminated
 * ASCII string holding its JSON representation excluding the beginning and
 * ending quote characters.
 *
 * @param source The string to be converted
 * @param target A buffer able to hold the converted string. It is safe to
 * assume that a buffer 6 times as large as the source buffer is sufficient.
 */
bool latin1_string_to_json(unsigned char* source, unsigned char* target) {
	unsigned char* s = source;
	unsigned char* t = target;
	while(*s) {
		unsigned char c = s[0];
		int intchar = c;
		for(int i=0;i<8;i++) {
			if(c=="\"\\/\b\f\n\r\t"[i]) {
				t[0] = '\\';
				t[1] = "\"\\/bfnrt"[i];
				t+=2;
				s++;
				break;
				continue;
			}
		}
		if(0<=c && c!=27 && c<=127) {
			*t = *s;
			t++;
			s++;
			continue;
		}
		else if((128<=c && c<=255) || c==27) {
			sprintf(t, "\\u00%02X", c);
			t+=6;
			s++;
			continue;
		}
		return false;
	}
	*t = 0;
	return true;
}
