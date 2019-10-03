# Requires python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# Legal: See COPYING.txt

import sys, json, time, itertools, libkeyboa.data as data

# Most functons in this module return transformations. retgen is a decorator for
# making a functon of no arguments return the supplied transformation
def retgen(transformation):
	def returntransformation():
		return transformation
	return returntransformation

# Input events. The inputformat argument can be
# - keyboa: The format written by listenkey.exe on Windows
# - x11vnc: The format written by `x11vnc -pipeinput` under X11
# - autodetect: keyboa or x11vnc depending on the first line
# In any case, the chosen inputformat will be communicated in an "inputformat"
# event.
def input_events(inputformat="autodetect", file=sys.stdin):
	def input_events_keyboa_format(gen):
		yield {"type":"inputformat","inputformat":"keyboa"}
		for line in gen:
			yield json.loads(line)
	def input_events_x11vnc_format(gen):
		yield {"type":"inputformat","inputformat":"x11vnc"}
		for line in gen:
			if(line.startswith('#')): # comment
				pass
			elif(line.startswith('Pointer ')):
				line=line.split(" ")
				line[1:5]=map(int, line[1:5])
				[_, client_id, xpos, ypos, mask, hint] = line
				buttonid=1
				buttonsdown=set()
				while(mask):
					if(mask&1):
						buttonsdown.add(buttonid)
						mask-=1
					buttonid+=1
					mask>>=1
				yield {
					"type": "pointerstate",
					"vnc_client_id": int(client_id),
					"x11_xpos": int(xpos),
					"x11_ypos": int(ypos),
					"x11_buttonsdown": buttonsdown,
					"vnc_hint": hint,
					}
			elif(line.startswith('Keysym ')):
				line=line.split(" ")
				line[1:4]=map(int, line[1:4])
				[_, client_id, down, keysym, keysym_symbol, hint] = line
				yield {
					"type": "keydown" if down else "keyup",
					"vnc_client_id": int(client_id),
					"x11_keysym": int(keysym),
					"x11_keysym_symbol": keysym_symbol,
					"vnc_hint": hint,
					}
			else:
				raise Exception("Unknown x11vnc event")
	def input_events_autodetect_format(gen):
		firstline=next(gen)
		restored_gen=itertools.chain([firstline], gen)
		if(firstline.startswith('{')):
			yield from input_events_keyboa_format(restored_gen)
		elif(firstline.startswith('#') or
		     firstline.startswith('Pointer ') or
		     firstline.startswith('Keysym ')):
			yield from input_events_x11vnc_format(restored_gen)
		else:
			raise Exception("Couldn't detect input format")
	def ret(_):
		gen=file
		try:
			if(inputformat=="autodetect"):
				yield from input_events_autodetect_format(gen)
			elif(inputformat=="keyboa"):
				yield from input_events_keyboa_format(gen)
			elif(inputformat=="x11vnc"):
				yield from input_events_x11vnc_format(gen)
			else:
				raise Exception("Illegal input format specified: "+str(inputformat))
		except KeyboardInterrupt:
			pass
		finally:
			yield {"type":"exit"}
	return ret

@retgen
def add_commonname(gen):
	for obj in gen:
		if(obj["type"] in ["keydown", "keyup", "keypress"]):
			if("win_virtualkey" in obj):
				vko=data.vkeyinfo(obj["win_virtualkey"])
				obj={**obj,"commonname":
					 vko["commonname_obj"]["commonname"]
					 if("commonname_obj" in vko)
					 else vko["win_virtualkey_symbol"]}
			elif("x11_keysym" in obj):
				kso=data.keysyminfo(obj["x11_keysym"])
				obj={**obj,"commonname":
					 kso["commonname_obj"]["commonname"]
					 if("commonname_obj" in kso)
					 else kso["x11_keysym_symbol"]}
		yield obj

@retgen
def resolve_commonname(gen):
	for obj in gen:
		if(obj["type"] in ["keydown", "keyup", "keypress"] and
		   "commonname" in obj):
			ret={**obj} # Shallow copy
			cn=obj["commonname"]
			cno=data.commonnameinfo(cn)
			if(cno):
				if("vkey_obj" in cno):
					ret={**ret,**cno["vkey_obj"]}
				if("keysym_obj" in cno):
					ret={**ret,**cno["keysym_obj"]}
			else:
				ret={**ret,
					 **data.vkeyinfo(cn),
					 **data.keysyminfo(cn),
					 }
			yield ret
		else:
			yield obj

# Output events. The outputformat argument can be
# - keyboa: The format read by sendkey.exe on Windows
# - xdotool: The format read by `xdotool -` under X11
# - autodetect:
#    - keyboa if input format is keyboa
#    - xdotool if input format is x11vnc
def output_events(outputformat="autodetect", file=sys.stdout):
	def output_events_keyboa_format(gen):
		for obj in gen:
			if(obj["type"]=="output"):
				obj=obj["data"]
			if(obj["type"] in ["keydown", "keyup", "keypress"]):
				event={}
				send=False
				for field in ["type", "win_scancode", "win_virtualkey",
				              "win_extended", "unicode_codepoint"]:
					if(field in obj and obj[field]):
						event[field]=obj[field]
						if(field in ["win_virtualkey",
									 "win_scancode",
									 "unicode_codepoint"]):
							send=True
				if(("win_virtualkey" in event
				    or "win_scancode" in event)
				   and "unicode_codepoint" in event):
					del event["unicode_codepoint"]
				if(send):
					json.dump(event, file, allow_nan=False, separators=(',',':'))
					print(file=file, flush=True)
			yield obj
	def output_events_xdotool_format(gen):
		pos=[None, None]
		but=set()
		for obj in gen:
			if(obj["type"]=="output"):
				obj=obj["data"]
			t=obj["type"]
			if(t in ["keydown", "keyup", "keypress"]):
				# Find missing keysym for a codepoint if possible
				if("x11_keysym" not in obj and
				   "x11_keysym_symbol" not in obj and
				   "unicode_codepoint" in obj):
					cp=obj["unicode_codepoint"]
					cpkey=data.format_unicode(cp)
					ksobj=data.keysyminfo(cpkey)
					obj={**obj, **ksobj}
				cp=obj["unicode_codepoint"] if "unicode_codepoint" in obj else None
				# Output using codepoint if present
				if(t=="keypress" and cp and cp>=0x30):
					print("type '"+chr(cp)+"'", file=file, flush=True)
				# Otherwise output using keysym or keysym_symbol
				elif("x11_keysym" in obj or
				   "x11_keysym_symbol" in obj):
					print(
						t.replace("press","") + " " +
						(hex(obj["x11_keysym"])
						 if "x11_keysym" in obj
						 else obj["x11_keysym_symbol"]),
						file=file,
						flush=True)
			elif(t=="pointerstate"):
				new_pos=[obj["x11_xpos"], obj["x11_ypos"]]
				if(pos!=new_pos):
					pos=new_pos
					print("mousemove "+str(pos[0])+" "+str(pos[1]),
						  file=file, flush=True)
				new_but=obj["x11_buttonsdown"]
				if(but!=new_but):
					for b in but.difference(new_but):
						print("mouseup "+str(b), file=file, flush=True)
					for b in new_but.difference(but):
						print("mousedown "+str(b), file=file, flush=True)
					but=new_but
			yield obj
	def output_events_autodetect_format(gen):
		# Find out what input format was used
		inputformat=None
		for obj in gen:
			if(obj["type"]=="output"):
				obj=obj["data"]
			t=obj["type"]
			if(t in ["keydown", "keyup", "keypress", "pointerstate"]):
				raise Exception("Event with type "+t+" before inputformat message")
			if(t=="inputformat"):
				inputformat=obj["inputformat"]
				yield obj
				break
			yield obj
		# Output using the detected format
		if(inputformat=="keyboa"):
			yield from output_events_keyboa_format(gen)
		elif(inputformat=="x11vnc"):
			yield from output_events_xdotool_format(gen)
		else:
			raise Exception("Couldn't determine output format")
	if(outputformat=="autodetect"):
		return output_events_autodetect_format
	elif(outputformat=="keyboa"):
		return output_events_keyboa_format
	elif(outputformat=="xdotool"):
		return output_events_xdotool_format
	else:
		raise Exception("Illegal output format specified: "+str(outputformat))

# A transformation that changes nothing while printing everything to stderr
def debug(file=sys.stderr):
	def ret(gen):
		for obj in gen:
			print(obj, file=file, flush=True)
			yield obj
	return ret

# A transformation that changes nothing while printing everything to stderr in
# json format
def debug_json(file=sys.stderr):
	def ret(gen):
		for obj in gen:
			json.dump(obj, file, allow_nan=False, indent=1)
			print(file=file, flush=True)
			yield obj
	return ret

# Only has effect on windows.
# If possible, find out what keys are already down at the start of the stream,
# and release them by sending keyup events encapsulated so that no
# transformation meddles with them until the output
@retgen
def releaseall_at_init(gen):
	for obj in gen:
		yield obj
		if(obj["type"]=="init" and
		   "vkeysdown" in obj):
			for key in obj["vkeysdown"]:
				yield {"type": "output", "data": {"type": "keyup", "win_virtualkey": key}}

# Dictionaries/lists aren't natively hashable
def hashobj(obj):
	return hash(json.dumps(obj,sort_keys=True,separators=(',',':')))

# Only has effect on windows.
# Add a few fields to key events:
# - physkey: Based on scancode and extended flag. Identifies a physical key on
#   the keyboard.
# - keyid: Based on scancode, extended flag, and virtualkey. Identifies a
#   physical key on the keyboard given a certain keyboard layout setting.
# - keyname_local: The name of the physical key in current localization.
# - win_virtualkey_symbol: A symbol representing win_virtualkey
# - win_virtualkey_description: A description/comment for win_virtualkey
# - delay: Number of milliseconds since the last key event
# Add a few fields to the init message if possible:
# - keyboard_hash: A value that stays the same for the same physical keyboard and
#   layout but likely changes otherwise, useful for making portable
#   configurations.
# - keyboard_hw_hash: A value that stays the same for the same physical keyboard
#   even under layout changes but likely changes otherwise, useful for making
#   portable configurations.
# - physkey_keyname_dict: A dictionary mapping physkey values to layout-specific
#   key names.
@retgen
def enrich_input(gen):
	initmsg = {}
	physkey_keyname_dict = {}
	prev_win_time=None
	for obj in gen:
		if(obj["type"]=="init" and obj["platform"]=="windows" and
		   set(["platform","keyboard_type","keyboard_subtype","function_keys",
				"OEMCP","key_names","oem_mapping"]) < obj.keys()):
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
				"keyboard_hw_hash": hashobj(kb_phys),
				}
		elif(obj["type"] in ["keydown", "keyup", "keypress"] and
			 set(["win_extended", "win_scancode", "win_virtualkey"]) <
			 obj.keys()):
			ret={**obj} # Shallow copy
			ext="E" if obj["win_extended"] else "_"
			hexsc=str.format('{:04X}', obj["win_scancode"])
			hexvk=str.format('{:02X}', obj["win_virtualkey"])
			physkey=ext+hexsc
			ret["physkey"]=physkey
			ret["keyid"]=physkey+"."+hexvk
			if physkey in physkey_keyname_dict:
				ret["keyname_local"]=physkey_keyname_dict[physkey]
			vko=data.vkeyinfo(ret["win_virtualkey"])
			ret={**ret,
				"win_virtualkey_symbol": vko["win_virtualkey_symbol"],
				"win_virtualkey_description": vko["win_virtualkey_description"],
				}
			if("win_time" in ret):
				if(prev_win_time!=None):
					ret["delay"]=ret["win_time"]-prev_win_time
				prev_win_time=ret["win_time"]
			else:
				prev_win_time=None
			yield ret
		else:
			yield obj

# When a key is held down, the operating system sends repeated keydown events
# with no intervening keyup event. Most applications recognize this as a
# repetition. The events_to_chords transformation does not. Put the allow_repeat
# transformation before events_to_chords in order to let repeated keys cause
# repeated chords. The field argument designates what field to use for detection
# of repetition. "physkey" or "win_virtualkey" probably works fine for that.
def allow_repeat(field):
	def ret(gen):
		keysdown=set()
		for obj in gen:
			t=obj["type"]
			key=obj[field] if field in obj else None
			if(t in ["keydown", "keypress"] and key in keysdown):
				yield {**obj, "type":"keyup"}
			if(t=="keydown"):
				keysdown.add(key)
			if(t in ["keyup", "keypress"] and key in keysdown):
				keysdown.remove(key)
			yield obj
	return ret

# Workaround for keys getting stuck.
def unstick_keys(field, timeouts):
	def ret(gen):
		key_history_state=[]
		for obj in gen:
			t=obj["type"]
			this_time=time.monotonic()
			alreadyup=False
			for (deadline, key, event) in key_history_state:
				if(this_time>deadline):
					if(t=="keyup" and obj[field]==key):
						alreadyup=True
					yield {**event, "type":"keyup", "noop":True}
			key_history_state=[*filter(lambda x: x[0]<=deadline, key_history_state)]
			if(alreadyup):
				continue
			if(t=="keydown"):
				key=obj[field]
				if(key in timeouts):
					key_history_state=sorted([*filter(lambda x: x[1]!=key, key_history_state), (this_time+timeouts[key], key, obj)])
			if(t=="keyup"):
				key=obj[field]
				key_history_state=[*filter(lambda x: x[1]!=key, key_history_state)]
				if(obj[field] in timeouts):
					# Probably switched from a privileged window, so we tunnel
					# a key release through the rest of the processing, since
					# it is otherwise likely to be silenced.
					yield {"type":"output","data":obj}
			yield obj
	return ret


# Convert key events to chords. This allows any key to act as a modifier.
# An example:
#  Key event | Chord event
#   A down   | -
#   S down   | -
#   J down   | -
#   J up     | [A S J]
#   A up     | -
#   S up     | -
#
# The field argument designates what field to use for naming the keys in a
# chord.
# Note that all other fields are lost.
# This transformation also generates keyup_all events when all keys are
# released. This allows a subsequent chords_to_events transformation to leave
# modifiers pressed between chords roughly in the same way the user does, which
# is necessary e.g. for a functioning Alt+Tab switch.
def events_to_chords(field):
	def ret(gen):
		keysdown=[]
		def updateui():
			return {"type":"ui","data":{
				"events_to_chords.keysdown."+field:[*keysdown]}}
		yield updateui()
		mods=0
		for obj in gen:
			t=obj["type"]
			if(t=="keydown"):
				key=obj[field]
				if(key in keysdown):
					pass
				else:
					keysdown.append(key)
				yield updateui()
			elif(t=="keyup"):
				key=obj[field]
				if(key in keysdown):
					i=keysdown.index(key)
					if(mods<=i):
						if("noop" not in obj):
							yield {"type":"chord",
							       "chord":keysdown[:i+1],
								   }
							mods=i
					else:
						mods-=1
					keysdown.remove(key)
					yield updateui()
					if(len(keysdown)==0):
						yield {"type":"keyup_all"}
				else:
					pass
			elif(t=="exit"):
				yield {"type":"keyup_all"}
				yield obj
			else:
				yield obj
	return ret

# Load state from file if possible
def loadstate(filename):
	state=None
	def SJSON_decode_object(o):
		if '__set__' in o:
			return set(o['__set__'])
		return o
	try:
		with open(filename, "r") as file:
			state=json.loads(file.read(),
				object_hook=SJSON_decode_object)
	except: pass
	def ret(gen):
		if(state):
			yield {"type":"loadstate","data":state}
		for obj in gen: yield obj
	return ret

# Save state to file if filename is a string, otherwise do nothing
def savestate(filename):
	if(not filename):
		def ret(gen):
			yield from gen
		return ret
	class SJSONEncoder(json.JSONEncoder):
		def default(self, o):
			if isinstance(o, set):
				return {'__set__': sorted(o)}
			raise Exception("Unknown object type")
	def ret(gen):
		state={}
		for obj in gen:
			yield obj
			t=obj["type"]
			if(t=="loadstate"):
				state=obj["data"]
			if(t=="savestate"):
				state={**state,**(obj["data"])}
				with open(filename, "w") as file:
					sjsonstr=json.dumps(
						state,
						separators=(',',':'),
						sort_keys=True,
						cls=SJSONEncoder)
					file.write(sjsonstr)
	return ret

# Macro record/playback functionality. Macros are sequences of chords.
# macrotest(event, recording) is a function of an event and a bool indicating
# whether the current state is recording. During recording, it is supposed to
# return:
# - If the event means save: ["save", macroname] where macroname is a string
# - If the event means cancel recording: ["cancel", None]
# - If the event is to be recorded: ["recordable", event] where event is the
#   event to be recorded
# - Otherwise: [False, None]
# During waiting, it is supposed to return
# - If the event means playback: ["playback", macroname] where macroname is a
#   string
# - If the event means begin recording: ["record", None]
# - Otherwise: [False, None]
# If statekey is given, it is used to persist macros between sessions.
# ui events are generated to communicate state and state transitions.
# TRANSITION     ( FROMSTATE -> TOSTATE   )
# record         ( waiting   -> recording )
# save           ( recording -> waiting   )
# cancel         ( recording -> waiting   )
# playback       ( waiting   -> playback  )
# finishplayback ( playback  -> waiting   )
# emptyplayback  ( waiting   -> waiting   )
def macro(macrotest, statekey=None):
	def ret(gen):
		macros={}
		yield {"type":"ui","data":{
			"macro.state": "waiting"}}
		for obj in gen:
			if(obj["type"]=="loadstate" and statekey and
			   statekey in obj["data"]):
				macros=obj["data"][statekey]
			[mt_op, mt_arg]=macrotest(obj, False)
			if(mt_op=="record"):
				# Record macro
				newmacro=[]
				yield {"type":"ui","data":{
					"macro.state": "recording",
					"macro.transition": "record",
					}}
				for obj in gen:
					[mt2_op, mt2_arg]=macrotest(obj, True)
					if(mt2_op=="save"):
						# Save macro
						macros[mt2_arg]=newmacro
						if(len(newmacro)==0):
							del macros[mt2_arg]
						if(statekey):
							yield {"type":"savestate",
								"data":{statekey:macros}}
						yield {"type":"ui","data":{
							"macro.state": "waiting",
							"macro.transition": "save",
							"macro.key": mt2_arg,
							}}
						break
					elif(mt2_op=="cancel"):
						# Cancel recording
						yield {"type":"ui","data":{
							"macro.state": "waiting",
							"macro.transition": "cancel"}}
						break
					else:
						if(mt2_op=="recordable"):
							# Add processed event to recording
							newmacro.append(mt2_arg)
						# Pass-through unprocessed event
						yield obj
			elif(mt_op=="playback" and mt_arg in macros):
				# Playback existing macro
				yield {"type":"ui","data":{
					"macro.state": "playback",
					"macro.transition": "playback",
					"macro.key": mt_arg,
					}}
				yield from macros[mt_arg]
				yield {"type":"ui","data":{
					"macro.state": "waiting",
					"macro.transition": "finishplayback"}}
			elif(mt_op=="playback"):
				# Playback non-existing macro
				yield {"type":"ui","data":{
					"macro.state": "waiting",
					"macro.transition": "emptyplayback",
					"macro.key": mt_arg,
					}}
			else:
				# Pass-through when not in record or playback
				yield obj
	return ret

# Convert chords to key events.
# An example:
#  Chord
#   Alt+Tab    | Alt down, Tab down, Tab up
#   Alt+Tab    | Tab down, Tab up
#   Ctrl+Alt+P | Ctrl down, P down, P up
#  (keyup_all) | Alt up
#
# The field argument designates what field to populate using the key name
# present in the chord. This transformation leaves modifiers pressed until a
# keyup_all event or a chord event that does not include it as a modifier. This
# allows e.g a functioning Alt+Tab switch.
def chords_to_events(field):
	def ret(gen):
		keysdown=[]
		def updateui():
			return {"type":"ui","data":{
				"chords_to_events.keysdown."+field:[*keysdown]}}
		yield updateui()
		for obj in gen:
			t=obj["type"]
			if(t=="keyup_all"):
				for key in reversed(keysdown):
					yield {"type":"keyup", field: key}
				keysdown=[]
				yield updateui()
				yield obj
			elif(t=="chord"):
				chord=obj["chord"]
				chordmods=chord[:-1]
				chordkey=chord[-1]
				for key in reversed(keysdown):
					if(not key in chordmods):
						yield {"type":"keyup",
						       field: key}
						keysdown.remove(key)
				for key in chordmods:
					if(not key in keysdown):
						yield {"type":"keydown",
						       field: key}
						keysdown.append(key)
				repeat=1
				if("repeat" in obj):
					repeat=obj["repeat"]
				for _ in range(repeat):
					yield {"type":"keypress",
					       field: chordkey}
				yield updateui()
			else:
				yield obj
	return ret

# If the AltGr key is present, it causes the following problems:
# - It is reported as a combination of two key events.
# - One of the key events has a different scancode, but the same virtualkey as
#    left Ctrl.
# - Sometimes when consuming events, one of the keyup events is absent.
# The transformation altgr_workaround_input will detect whether AltGr is
# present, remove the offending key event and inform altgr_workaround_output.
# The transformation altgr_workaround_output will reinstate/create a correct key
# event if AltGr is present.
# The transformations between these two workarounds can then act on key events
# for RMENU (virtualkey 0xA5=165), which will mean AltGr if and only if it is
# present.
@retgen
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

@retgen
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
			sc=(obj["win_scancode"]
			    if "win_scancode" in obj else None)
			vk=obj["win_virtualkey"]
			t=obj["type"]
			altgr_lctrl_event={
				"type":t,
				"win_scancode": altgr_lctrl_sc,
				"win_extended": altgr_lctrl_ext,
				"win_virtualkey": lctrl,
				}
			if("win_time" in obj):
				altgr_lctrl_event["win_time"]=obj["win_time"]
			if(vk==lctrl and (not sc or sc<=0x200)):
				yield obj
			elif(vk==lctrl):
				pass
			elif(vk==rmenu and t in ["keydown", "keyup"]):
				yield altgr_lctrl_event
				yield obj
			else: # means (vk==rmenu and t=="keypress")
				yield {**altgr_lctrl_event, "type": "keydown"}
				yield {**obj, "type": "keydown"}
				yield {**altgr_lctrl_event, "type": "keyup"}
				yield {**obj, "type": "keyup"}
		else:
			yield obj

# Remove all events from the event stream except the given types.
def selecttypes(types):
	def ret(gen):
		for obj in gen:
			if obj["type"] in types:
				yield obj
	return ret

# Remove all events from the event stream of the given types.
def selecttypesexcept(types):
	def ret(gen):
		for obj in gen:
			if not obj["type"] in types:
				yield obj
	return ret

# Remove all fields from every event except the given fields.
def selectfields(fields):
	def ret(gen):
		for obj in gen:
			y={}
			for field in obj:
				if field in fields:
					y[field]=obj[field]
			yield y
	return ret

# Limit the rate of events to n events per second by making sure the delay
# between any two events is at least 1/n seconds. This does not insert any
# delay between events that already are sufficiently spread out. If filter is
# given, only apply to events that match that predicate.
#
# WARNING for use on Windows: When holding down a key, the Windows autorepeat
# functionality can produce up to at least 34 keydown events per second. Do not
# slow down your program so much that the consumption of input events is
# retarded below the rate the input events are generated. Doing so could cause
# Windows to stop sending events to listenkey.exe, which in turn would likely
# freeze your program.
def ratelimit(n, filter = lambda _: True):
	def ret(gen):
		minimum_delay=1/n
		last_time=0
		for obj in gen:
			if filter(obj):
				this_time=time.monotonic()
				wait=last_time+minimum_delay-this_time
				last_time=this_time
				if(wait>0):
					time.sleep(wait)
					last_time+=wait
			yield obj
	return ret

__all__ = [
	"keyboa_input",
	"add_commonname",
	"resolve_commonname",
	"keyboa_output",
	"debug",
	"debug_json",
	"releaseall_at_init",
	"enrich_input",
	"allow_repeat",
	"unstick_keys",
	"events_to_chords",
	"loadstate",
	"savestate",
	"macro",
	"chords_to_events",
	"altgr_workaround_input",
	"altgr_workaround_output",
	"selecttypes",
	"selecttypesexcept",
	"selectfields",
	"ratelimit",
	]
