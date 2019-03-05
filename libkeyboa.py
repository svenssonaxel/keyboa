# Requires python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# License: See LICENSE

import sys, json, functools

#Run data in series through the supplied list of transformations
def keyboa_run(tr):
	return functools.reduce((lambda x, y: y(x)), tr, None)

#Read events from stdin
def input(_):
	try:
		for line in sys.stdin:
			obj=json.loads(line)
			yield obj
	except KeyboardInterrupt:
		pass
	finally:
		yield {"type":"exit"}

#Output events to stdout
def output(gen):
	for obj in gen:
		json.dump(obj["data"] if obj["type"]=="output" else obj, sys.stdout, allow_nan=False, indent=1)
		print()
		sys.stdout.flush()

#A transformation that changes nothing while printing everything to stderr
def debug(gen):
	for obj in gen:
		json.dump(obj["data"] if obj["type"]=="output" else obj, sys.stderr, allow_nan=False, indent=1)
		#print() todo to stderr
		sys.stderr.flush()
		yield obj

#Find out what keys are already down at the start of the stream, and release
#them by sending keyup events encapsulated so that no transformation meddles
#with them until the output
def releaseall_at_init(gen):
	for obj in gen:
		yield obj
		if(obj["type"]=="init"):
			for key in obj["vkeysdown"]:
				yield {"type": "output", "data": {"type": "keyup", "win_virtualkey": key}}

#Dictionaries/lists aren't natively hashable
def hashobj(obj):
	return hash(json.dumps(obj,sort_keys=True,separators=(',',':')))

#Add a few fields to key events:
#- physkey: Based on scancode and extended flag. Identifies a physical key on
#  the keyboard.
#- keyid: Based on scancode, extended flag, and virtualkey. Identifies a
#  physical key on the keyboard given a certain keyboard layout setting.
#- keyname_local: The name of the physical key in current localization.
#- win_virtualkey_symbol: A symbol representing win_virtualkey
#- win_virtualkey_description: A description/comment for win_virtualkey
#Also add a few fields to the init message:
#- keyboard_hash: A value that stays the same for the same physical keyboard and
#  layout but likely changes otherwise, useful for making portable
#  configurations.
#- keyboard_hw_hash: A value that stays the same for the same physical keyboard
#  even under layout changes but likely changes otherwise, useful for making
#  portable configurations.
#- physkey_keyname_dict: A dictionary mapping physkey values to layout-specific
#  key names.
def enrich_input(gen):
	initmsg = {}
	physkey_keyname_dict = {}
	for obj in gen:
		if obj["type"]=="init":
			initmsg=obj
			for q in obj["key_names"]:
				ext="E" if q["extended"] else "_"
				hexsc=str.format('{:04X}', q["scancode"])
				physkey=ext+hexsc
				physkey_keyname_dict[physkey]=q["keyname"]
			kb_phys={field:obj[field] for field in
				["platform","keyboard_type","keyboard_subtype","function_keys"]}
			kb_layout={**kb_phys,**{field:obj[field] for field in
				["OEMCP","key_names","oem_mapping"]}}
			#"active_input_locale_current_thread":69010461,"available_input_locales":[69010461],
			yield {**obj,
				"physkey_keyname_dict":physkey_keyname_dict,
				"keyboard_hash": hashobj(kb_layout),
				"keyboard_hw_hash": hashobj(kb_phys)}
		elif obj["type"] in ["keydown", "keyup", "keypress"]:
			ret={**obj} #Shallow copy
			ext="E" if obj["win_extended"] else "_"
			hexsc=str.format('{:04X}', obj["win_scancode"])
			hexvk=str.format('{:02X}', obj["win_virtualkey"])
			physkey=ext+hexsc
			ret["physkey"]=physkey
			ret["keyid"]=physkey+"."+hexvk
			if physkey in physkey_keyname_dict:
				ret["keyname_local"]=physkey_keyname_dict[physkey]
			ret={**ret,**vkeyinfo(ret["win_virtualkey"])}
			yield ret
		else:
			yield obj

#When a key is held down, the operating system sends repeated keydown events
#with no intervening keyup event. Most applications recognize this as a
#repetition. The events_to_chords transformation does not. Put the allow_repeat
#transformation before events_to_chords in order to let repeated keys cause
#repeated chords. The field argument designates what field to use for detection
#of repetition. "physkey" or "win_virtualkey" probably works fine for that.
def allow_repeat(field):
	def ret(gen):
		keysdown=set()
		for obj in gen:
			type=obj["type"]
			key=obj[field] if field in obj else None
			if(type in ["keydown", "keypress"] and key in keysdown):
				yield {**obj, "type":"keyup"}
			if(type=="keydown"):
				keysdown.add(key)
			if(type in ["keyup", "keypress"] and key in keysdown):
				keysdown.remove(key)
			yield obj
	return ret

#Convert key events to chords. This allows any key to act as a modifier.
#An example:
# Key event | Chord event
#  A down   | -
#  S down   | -
#  J down   | -
#  J up     | [A S J]
#  A up     | -
#  S up     | -
#
#The field argument designates what field to use for naming the keys in a chord.
#Note that all other fields are lost.
#This transformation also generates keyup_all events when all keys are released.
#This allows a subsequent chords_to_events transformation to leave modifiers
#pressed between chords roughly in the same way the user does, which is
#necessary e.g. for a functioning Alt+Tab switch.
def events_to_chords(field):
	def ret(gen):
		keysdown=[]
		mods=0
		for obj in gen:
			type=obj["type"]
			if(type=="keydown"):
				key=obj[field]
				if(key in keysdown):
					pass
				else:
					keysdown.append(key)
			elif(type=="keyup"):
				key=obj[field]
				if(key in keysdown):
					i=keysdown.index(key)
					if(mods<=i):
						yield {"type":"chord", "chord":keysdown[:i+1]}
						mods=i
					else:
						mods-=1
					keysdown.remove(key)
					if(len(keysdown)==0):
						yield {"type":"keyup_all"}
				else:
					pass
			elif(type=="exit"):
				yield {"type":"keyup_all"}
				yield obj
			else:
				yield obj
	return ret

#Convert chords to key events.
#An example:
# Chord 
#  Alt+Tab    | Alt down, Tab down, Tab up
#  Alt+Tab    | Tab down, Tab up
#  Ctrl+Alt+P | Ctrl down, P down, P up
# (keyup_all) | Alt up
#
#The field argument designates what field to populate using the key name present
#in the chord. This transformation leaves modifiers pressed until a keyup_all
#event or a chord event that does not include it as a modifier. This allows e.g
#a functioning Alt+Tab switch.
def chords_to_events(field):
	def ret(gen):
		keysdown=[]
		for obj in gen:
			type=obj["type"]
			if(type=="keyup_all"):
				for key in reversed(keysdown):
					yield {"type":"keyup", field: key}
				yield obj
				keysdown=[]
			elif(type=="chord"):
				chord=obj["chord"]
				chordmods=chord[:-1]
				chordkey=chord[-1]
				for key in reversed(keysdown):
					if(not key in chordmods):
						yield {"type":"keyup", field: key}
						keysdown.remove(key)
				for key in chordmods:
					if(not key in keysdown):
						yield {"type":"keydown", field: key}
						keysdown.append(key)
				repeat=1
				if("repeat" in obj):
					repeat=obj["repeat"]
				for _ in range(repeat):
					yield {"type":"keypress", field: chordkey}
			else:
				yield obj
	return ret

#Removes events and fields not necessary for output to sendkey. As an exception,
#events encapsulated by releaseall_at_init are still passed through.
def sendkey_cleanup(gen):
	for obj in gen:
		if(obj["type"] in ["keydown", "keyup", "keypress"]):
			event={}
			send=False
			for field in ["type", "win_scancode", "win_virtualkey", "win_extended", "unicode_codepoint"]:
				if(field in obj and obj[field]):
					event[field]=obj[field]
					if(field=="win_virtualkey" or field=="win_scancode" or field=="unicode_codepoint"):
						send=True
			if(send):
				yield event
		if(obj["type"]=="output"):
			yield obj

#If the AltGr key is present, it causes the following problems:
#- It is reported as a combination of two key events.
#- One of the key events has a different scancode, but the same virtualkey as
#   left Ctrl.
#- Sometimes when consuming events, one of the keyup events is absent.
#The transformation altgr_workaround_input will detect whether AltGr is present,
#remove the offending key event and inform altgr_workaround_output.
#The transformation altgr_workaround_output will reinstate/create a correct key
#event if AltGr is present.
#The transformations between these two workarounds can then act on key events
#for RMENU (virtualkey 0xA5=165), which will mean AltGr if and only if it is present.

def altgr_workaround_input(gen):
	lctrl=0xA2
	rmenu=0xA5
	altgr_present=False
	altgr_lctrl_sc=None
	for obj in gen:
		if(obj["type"] in ["keydown", "keyup"]
		   and "win_scancode" in obj
		   and "win_virtualkey" in obj
		   and obj["win_virtualkey"] in [lctrl, rmenu]
		   and "win_time" in obj):
			sc=obj["win_scancode"]
			vk=obj["win_virtualkey"]
			if(not altgr_present and sc>0x200 and vk==lctrl):
				altgr_present=True
				altgr_lctrl_sc=sc
				yield {"type": "altgr_present", "win_scancode": sc, "win_extended": obj["win_extended"]}
			if(not (altgr_present and obj["win_scancode"]==altgr_lctrl_sc and vk==lctrl)):
				yield obj
		else:
			yield obj

def altgr_workaround_output(gen):
	lctrl=0xA2
	rmenu=0xA5
	altgr_present=False
	altgr_lctrl_sc=None
	altgr_lctrl_ext=None
	for obj in gen:
		if(obj["type"]=="altgr_present"):
			altgr_present=True
			altgr_lctrl_sc=obj["win_scancode"]
			altgr_lctrl_ext=obj["win_extended"]
		elif(altgr_present
		     and obj["type"] in ["keydown", "keyup", "keypress"]
		     and "win_virtualkey" in obj
		     and obj["win_virtualkey"] in [lctrl, rmenu]):
			sc=obj["win_scancode"] if "win_scancode" in obj else None
			vk=obj["win_virtualkey"]
			type=obj["type"]
			altgr_lctrl_event={
				"type":type,
				"win_scancode": altgr_lctrl_sc,
				"win_extended": altgr_lctrl_ext,
				"win_virtualkey": lctrl}
			if("win_time" in obj):
				altgr_lctrl_event["win_time"]=obj["win_time"]
			if(vk==lctrl and (not sc or sc<=0x200)):
				yield obj
			elif(vk==lctrl):
				pass
			elif(vk==rmenu and type in ["keydown", "keyup"]):
				yield altgr_lctrl_event
				yield obj
			else: #means (vk==rmenu and type=="keypress")
				yield {**altgr_lctrl_event, "type": "keydown"}
				yield {**obj, "type": "keydown"}
				yield {**altgr_lctrl_event, "type": "keyup"}
				yield {**obj, "type": "keyup"}
		else:
			yield obj

#Remove all events from the event stream except the given types.
def selecttypes(types):
	def ret(gen):
		for obj in gen:
			if obj["type"] in types:
				yield obj
	return ret

#Remove all fields from every event except the given fields.
def selectfields(fields):
	def ret(gen):
		for obj in gen:
			y={}
			for field in obj:
				if field in fields:
					y[field]=obj[field]
			yield y
	return ret

#The following is a table of windows virtual keys. It can be accessed through
#the vkeyinfo function using either a numeric or symbolic virtual key. It
#returns a dictionary with the fields win_virtualkey, win_virtualkey_symbol, and
#win_virtualkey_description.

_vkeystable = [
	#Vkey,  Symbol,                    Description
	(0x01, "VK_LBUTTON",              "Left mouse button"),
	(0x02, "VK_RBUTTON",              "Right mouse button"),
	(0x03, "VK_CANCEL",               "Control-break (Ctrl+Pause)"),
	(0x04, "VK_MBUTTON",              "Middle mouse button"),
	(0x05, "VK_XBUTTON1",             "X1 mouse button"),
	(0x06, "VK_XBUTTON2",             "X2 mouse button"),
	(0x07, None,                      "Undefined"),
	(0x08, "VK_BACK",                 "BACKSPACE key"),
	(0x09, "VK_TAB",                  "TAB key"),
	(0x0A, None,                      "Reserved"),
	(0x0B, None,                      "Reserved"),
	(0x0C, "VK_CLEAR",                "CLEAR key (Shift+Num5)"),
	(0x0D, "VK_RETURN",               "ENTER key"),
	(0x0E, None,                      "Undefined"),
	(0x0F, None,                      "Undefined"),
	(0x10, "VK_SHIFT",                "SHIFT key"),
	(0x11, "VK_CONTROL",              "CTRL key"),
	(0x12, "VK_MENU",                 "ALT key"),
	(0x13, "VK_PAUSE",                "PAUSE key"),
	(0x14, "VK_CAPITAL",              "CAPS LOCK key"),
	(0x15, "VK_KANA",                 "IME Kana mode"),
	(0x15, "VK_HANGUEL",              "IME Hanguel mode"),
	(0x15, "VK_HANGUL",               "IME Hangul mode"),
	(0x16, None,                      "Undefined"),
	(0x17, "VK_JUNJA",                "IME Junja mode"),
	(0x18, "VK_FINAL",                "IME final mode"),
	(0x19, "VK_HANJA",                "IME Hanja mode"),
	(0x19, "VK_KANJI",                "IME Kanji mode"),
	(0x1A, None,                      "Undefined"),
	(0x1B, "VK_ESCAPE",               "ESC key"),
	(0x1C, "VK_CONVERT",              "IME convert"),
	(0x1D, "VK_NONCONVERT",           "IME nonconvert"),
	(0x1E, "VK_ACCEPT",               "IME accept"),
	(0x1F, "VK_MODECHANGE",           "IME mode change request"),
	(0x20, "VK_SPACE",                "SPACEBAR"),
	(0x21, "VK_PRIOR",                "PAGE UP key"),
	(0x22, "VK_NEXT",                 "PAGE DOWN key"),
	(0x23, "VK_END",                  "END key"),
	(0x24, "VK_HOME",                 "HOME key"),
	(0x25, "VK_LEFT",                 "LEFT ARROW key"),
	(0x26, "VK_UP",                   "UP ARROW key"),
	(0x27, "VK_RIGHT",                "RIGHT ARROW key"),
	(0x28, "VK_DOWN",                 "DOWN ARROW key"),
	(0x29, "VK_SELECT",               "SELECT key"),
	(0x2A, "VK_PRINT",                "PRINT key"),
	(0x2B, "VK_EXECUTE",              "EXECUTE key"),
	(0x2C, "VK_SNAPSHOT",             "PRINT SCREEN key"),
	(0x2D, "VK_INSERT",               "INS key"),
	(0x2E, "VK_DELETE",               "DEL key"),
	(0x2F, "VK_HELP",                 "HELP key"),
	(0x30, None,                      "0 key"),
	(0x31, None,                      "1 key"),
	(0x32, None,                      "2 key"),
	(0x33, None,                      "3 key"),
	(0x34, None,                      "4 key"),
	(0x35, None,                      "5 key"),
	(0x36, None,                      "6 key"),
	(0x37, None,                      "7 key"),
	(0x38, None,                      "8 key"),
	(0x39, None,                      "9 key"),
	(0x3A, None,                      "Undefined"),
	(0x3B, None,                      "Undefined"),
	(0x3C, None,                      "Undefined"),
	(0x3D, None,                      "Undefined"),
	(0x3E, None,                      "Undefined"),
	(0x3F, None,                      "Undefined"),
	(0x40, None,                      "Undefined"),
	(0x41, None,                      "A key"),
	(0x42, None,                      "B key"),
	(0x43, None,                      "C key"),
	(0x44, None,                      "D key"),
	(0x45, None,                      "E key"),
	(0x46, None,                      "F key"),
	(0x47, None,                      "G key"),
	(0x48, None,                      "H key"),
	(0x49, None,                      "I key"),
	(0x4A, None,                      "J key"),
	(0x4B, None,                      "K key"),
	(0x4C, None,                      "L key"),
	(0x4D, None,                      "M key"),
	(0x4E, None,                      "N key"),
	(0x4F, None,                      "O key"),
	(0x50, None,                      "P key"),
	(0x51, None,                      "Q key"),
	(0x52, None,                      "R key"),
	(0x53, None,                      "S key"),
	(0x54, None,                      "T key"),
	(0x55, None,                      "U key"),
	(0x56, None,                      "V key"),
	(0x57, None,                      "W key"),
	(0x58, None,                      "X key"),
	(0x59, None,                      "Y key"),
	(0x5A, None,                      "Z key"),
	(0x5B, "VK_LWIN",                 "Left Windows key"),
	(0x5C, "VK_RWIN",                 "Right Windows key"),
	(0x5D, "VK_APPS",                 "Applications key"),
	(0x5E, None,                      "Reserved"),
	(0x5F, "VK_SLEEP",                "Computer Sleep key"),
	(0x60, "VK_NUMPAD0",              "Numeric keypad 0 key"),
	(0x61, "VK_NUMPAD1",              "Numeric keypad 1 key"),
	(0x62, "VK_NUMPAD2",              "Numeric keypad 2 key"),
	(0x63, "VK_NUMPAD3",              "Numeric keypad 3 key"),
	(0x64, "VK_NUMPAD4",              "Numeric keypad 4 key"),
	(0x65, "VK_NUMPAD5",              "Numeric keypad 5 key"),
	(0x66, "VK_NUMPAD6",              "Numeric keypad 6 key"),
	(0x67, "VK_NUMPAD7",              "Numeric keypad 7 key"),
	(0x68, "VK_NUMPAD8",              "Numeric keypad 8 key"),
	(0x69, "VK_NUMPAD9",              "Numeric keypad 9 key"),
	(0x6A, "VK_MULTIPLY",             "Multiply key"),
	(0x6B, "VK_ADD",                  "Add key"),
	(0x6C, "VK_SEPARATOR",            "Separator key"),
	(0x6D, "VK_SUBTRACT",             "Subtract key"),
	(0x6E, "VK_DECIMAL",              "Decimal key"),
	(0x6F, "VK_DIVIDE",               "Divide key"),
	(0x70, "VK_F1",                   "F1 key"),
	(0x71, "VK_F2",                   "F2 key"),
	(0x72, "VK_F3",                   "F3 key"),
	(0x73, "VK_F4",                   "F4 key"),
	(0x74, "VK_F5",                   "F5 key"),
	(0x75, "VK_F6",                   "F6 key"),
	(0x76, "VK_F7",                   "F7 key"),
	(0x77, "VK_F8",                   "F8 key"),
	(0x78, "VK_F9",                   "F9 key"),
	(0x79, "VK_F10",                  "F10 key"),
	(0x7A, "VK_F11",                  "F11 key"),
	(0x7B, "VK_F12",                  "F12 key"),
	(0x7C, "VK_F13",                  "F13 key"),
	(0x7D, "VK_F14",                  "F14 key"),
	(0x7E, "VK_F15",                  "F15 key"),
	(0x7F, "VK_F16",                  "F16 key"),
	(0x80, "VK_F17",                  "F17 key"),
	(0x81, "VK_F18",                  "F18 key"),
	(0x82, "VK_F19",                  "F19 key"),
	(0x83, "VK_F20",                  "F20 key"),
	(0x84, "VK_F21",                  "F21 key"),
	(0x85, "VK_F22",                  "F22 key"),
	(0x86, "VK_F23",                  "F23 key"),
	(0x87, "VK_F24",                  "F24 key"),
	(0x88, None,                      "Unassigned"),
	(0x89, None,                      "Unassigned"),
	(0x8A, None,                      "Unassigned"),
	(0x8B, None,                      "Unassigned"),
	(0x8C, None,                      "Unassigned"),
	(0x8D, None,                      "Unassigned"),
	(0x8E, None,                      "Unassigned"),
	(0x8F, None,                      "Unassigned"),
	(0x90, "VK_NUMLOCK",              "NUM LOCK key"),
	(0x91, "VK_SCROLL",               "SCROLL LOCK key"),
	(0x92, None,                      "OEM specific"),
	(0x93, None,                      "OEM specific"),
	(0x94, None,                      "OEM specific"),
	(0x95, None,                      "OEM specific"),
	(0x96, None,                      "OEM specific"),
	(0x97, None,                      "Unassigned"),
	(0x98, None,                      "Unassigned"),
	(0x99, None,                      "Unassigned"),
	(0x9A, None,                      "Unassigned"),
	(0x9B, None,                      "Unassigned"),
	(0x9C, None,                      "Unassigned"),
	(0x9D, None,                      "Unassigned"),
	(0x9E, None,                      "Unassigned"),
	(0x9F, None,                      "Unassigned"),
	(0xA0, "VK_LSHIFT",               "Left SHIFT key"),
	(0xA1, "VK_RSHIFT",               "Right SHIFT key"),
	(0xA2, "VK_LCONTROL",             "Left CONTROL key"),
	(0xA3, "VK_RCONTROL",             "Right CONTROL key"),
	(0xA4, "VK_LMENU",                "Left MENU key"),
	(0xA5, "VK_RMENU",                "Right MENU key"),
	(0xA6, "VK_BROWSER_BACK",         "Browser Back key"),
	(0xA7, "VK_BROWSER_FORWARD",      "Browser Forward key"),
	(0xA8, "VK_BROWSER_REFRESH",      "Browser Refresh key"),
	(0xA9, "VK_BROWSER_STOP",         "Browser Stop key"),
	(0xAA, "VK_BROWSER_SEARCH",       "Browser Search key"),
	(0xAB, "VK_BROWSER_FAVORITES",    "Browser Favorites key"),
	(0xAC, "VK_BROWSER_HOME",         "Browser Start and Home key"),
	(0xAD, "VK_VOLUME_MUTE",          "Volume Mute key"),
	(0xAE, "VK_VOLUME_DOWN",          "Volume Down key"),
	(0xAF, "VK_VOLUME_UP",            "Volume Up key"),
	(0xB0, "VK_MEDIA_NEXT_TRACK",     "Next Track key"),
	(0xB1, "VK_MEDIA_PREV_TRACK",     "Previous Track key"),
	(0xB2, "VK_MEDIA_STOP",           "Stop Media key"),
	(0xB3, "VK_MEDIA_PLAY_PAUSE",     "Play/Pause Media key"),
	(0xB4, "VK_LAUNCH_MAIL",          "Start Mail key"),
	(0xB5, "VK_LAUNCH_MEDIA_SELECT",  "Select Media key"),
	(0xB6, "VK_LAUNCH_APP1",          "Start Application 1 key"),
	(0xB7, "VK_LAUNCH_APP2",          "Start Application 2 key"),
	(0xB8, None,                      "Reserved"),
	(0xB9, None,                      "Reserved"),
	(0xBA, "VK_OEM_1",                "Used for miscellaneous characters; it can vary by keyboard. For the US standard keyboard, the ';:' key"),
	(0xBB, "VK_OEM_PLUS",             "For any country/region, the '+' key"),
	(0xBC, "VK_OEM_COMMA",            "For any country/region, the ',' key"),
	(0xBD, "VK_OEM_MINUS",            "For any country/region, the '-' key"),
	(0xBE, "VK_OEM_PERIOD",           "For any country/region, the '.' key"),
	(0xBF, "VK_OEM_2",                "Used for miscellaneous characters; it can vary by keyboard. For the US standard keyboard, the '/?' key"),
	(0xC0, "VK_OEM_3",                "Used for miscellaneous characters; it can vary by keyboard. For the US standard keyboard, the '`~' key"),
	(0xC1, None,                      "Reserved"),
	(0xC2, None,                      "Reserved"),
	(0xC3, None,                      "Reserved"),
	(0xC4, None,                      "Reserved"),
	(0xC5, None,                      "Reserved"),
	(0xC6, None,                      "Reserved"),
	(0xC7, None,                      "Reserved"),
	(0xD8, None,                      "Unassigned"),
	(0xD9, None,                      "Unassigned"),
	(0xDA, None,                      "Unassigned"),
	(0xDB, "VK_OEM_4",                "Used for miscellaneous characters; it can vary by keyboard. For the US standard keyboard, the '[{' key"),
	(0xDC, "VK_OEM_5",                "Used for miscellaneous characters; it can vary by keyboard. For the US standard keyboard, the '\|' key"),
	(0xDD, "VK_OEM_6",                "Used for miscellaneous characters; it can vary by keyboard. For the US standard keyboard, the ']}' key"),
	(0xDE, "VK_OEM_7",                "Used for miscellaneous characters; it can vary by keyboard. For the US standard keyboard, the (', gle-quote/double-quote' key"),
	(0xDF, "VK_OEM_8",                "Used for miscellaneous characters; it can vary by keyboard."),
	(0xE0, None,                      "Reserved"),
	(0xE1, None,                      "OEM specific"),
	(0xE2, "VK_OEM_102",              "Either the angle bracket key or the backslash key on the RT 102-key keyboard"),
	(0xE3, None,                      "OEM specific"),
	(0xE4, None,                      "OEM specific"),
	(0xE5, "VK_PROCESSKEY",           "IME PROCESS key"),
	(0xE6, None,                      "OEM specific"),
	(0xE7, "VK_PACKET",               "Used to pass Unicode characters as if they were keystrokes."),
	(0xE8, None,                      "Unassigned"),
	(0xE9, None,                      "OEM specific"),
	(0xEA, None,                      "OEM specific"),
	(0xEB, None,                      "OEM specific"),
	(0xEC, None,                      "OEM specific"),
	(0xED, None,                      "OEM specific"),
	(0xEE, None,                      "OEM specific"),
	(0xEF, None,                      "OEM specific"),
	(0xF0, None,                      "OEM specific"),
	(0xF1, None,                      "OEM specific"),
	(0xF2, None,                      "OEM specific"),
	(0xF3, None,                      "OEM specific"),
	(0xF4, None,                      "OEM specific"),
	(0xF5, None,                      "OEM specific"),
	(0xF6, "VK_ATTN",                 "Attn key"),
	(0xF7, "VK_CRSEL",                "CrSel key"),
	(0xF8, "VK_EXSEL",                "ExSel key"),
	(0xF9, "VK_EREOF",                "Erase EOF key"),
	(0xFA, "VK_PLAY",                 "Play key"),
	(0xFB, "VK_ZOOM",                 "Zoom key"),
	(0xFC, "VK_NONAME",               "Reserved for future use"),
	(0xFD, "VK_PA1",                  "PA1 key"),
	(0xFE, "VK_OEM_CLEAR",            "Clear key")]

_vkeysdict={}
for (win_virtualkey, win_virtualkey_symbol, win_virtualkey_description) in _vkeystable:
	item={
		"win_virtualkey": win_virtualkey,
		"win_virtualkey_symbol": win_virtualkey_symbol,
		"win_virtualkey_description": win_virtualkey_description}
	if(win_virtualkey):
		_vkeysdict[win_virtualkey]=item
	if(win_virtualkey_symbol):
		_vkeysdict[win_virtualkey_symbol]=item
del _vkeystable

def vkeyinfo(vkey):
	try:
		return _vkeysdict[vkey]
	except KeyError:
		return {}
