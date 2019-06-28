# Requires python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# License: See LICENSE

import sys, json, functools, time, csv

# Run data in series through the supplied list of transformations
def keyboa_run(tr):
	def reducer(reduced, next_generator):
		return next_generator(reduced)
	reduced_transformation = functools.reduce(reducer, tr, [])
	for _ in reduced_transformation:
		pass

# Read events from stdin. Auto-detect source format and adjust accordingly.
# Supported formats are:
# - The JSON output of listenkey.exe
# - The format of x11vnc -pipeinput
# After detecting the format, inform any downstream output processor so it can
# match output format, then begin producing events from source.
def input(_):
	try:
		firstline=sys.stdin.readline()
		if(firstline.startswith('{')):
			# listenkey.exe format
			obj=json.loads(firstline)
			# listenkey.exe may or may not print an init message. At a minimum,
			# the output generator needs to know what format to print.
			if(not obj["type"]=="init"):
				yield {
					"type": "init",
					"platform": "windows"}
			yield obj
			for line in sys.stdin:
				obj=json.loads(line)
				yield obj
		elif(firstline.startswith('#')):
			# x11vnc format
			yield {
				"type": "init",
				"platform": "vnc"}
			for line in sys.stdin:
				if(line.startswith('#')): # comment
					pass
				elif(line.startswith('Pointer ')):
					line=line.split(" ")
					line[1:5]=map(int, line[1:5])
					[_, client_id, xpos, ypos, mask, hint] = line
					buttonid=1
					buttonsdown=set()
					while(mask>0):
						if(mask&1):
							buttonsdown.add(buttonid)
							buttonid+=1
							mask-=1
						mask/=2
					yield {
						"type": "pointerstate",
						"vnc_client_id": int(client_id),
						"vnc_xpos": int(xpos),
						"vnc_ypos": int(ypos),
						"vnc_buttonsdown": buttonsdown,
						"vnc_hint": hint}
				elif(line.startswith('Keysym ')):
					line=line.split(" ")
					line[1:4]=map(int, line[1:4])
					[_, client_id, down, keysym, keysym_symbol, hint] = line
					yield {
						"type": "keydown" if down else "keyup",
						"vnc_client_id": int(client_id),
						"x11_keysym": int(keysym),
						"x11_keysym_symbol": keysym_symbol,
						"vnc_hint": hint}
				else:
					raise Exception("Unknown x11vnc event")
		else:
			raise Exception("Unknown format")
	except KeyboardInterrupt:
		pass
	finally:
		yield {"type":"exit"}

def add_commonname(gen):
	for obj in gen:
		if(obj["type"] in ["keydown", "keyup", "keypress"]):
			if("win_virtualkey" in obj):
				vko=vkeyinfo(obj["win_virtualkey"])
				obj={**obj,"commonname":
					 vko["commonname_obj"]["commonname"]
					 if("commonname_obj" in vko)
					 else vko["win_virtualkey_symbol"]}
			elif("x11_keysym" in obj):
				kso=keysyminfo(obj["x11_keysym"])
				obj={**obj,"commonname":
					 kso["commonname_obj"]["commonname"]
					 if("commonname_obj" in kso)
					 else kso["x11_keysym_symbol"]}
		yield obj

def resolve_commonname(gen):
	for obj in gen:
		if(obj["type"] in ["keydown", "keyup", "keypress"] and
		   "commonname" in obj):
			ret={**obj} # Shallow copy
			cn=obj["commonname"]
			if(cn in commonnamesdict):
				cno=commonnamesdict[cn]
				if("vkey_obj" in cno):
					ret={**ret,**cno["vkey_obj"]}
				if("keysym_obj" in cno):
					ret={**ret,**cno["keysym_obj"]}
			else:
				ret={**ret,
					 **vkeyinfo(cn),
					 **keysyminfo(cn)}
			yield ret
		else:
			yield obj

# Output events to stdout. Detect format announced by input() and adjust
# accordingly.
# Supported formats are:
# - The JSON format for sendkey.exe
# - The format of x11vnc -pipeinput
def output(gen):
	platform=None
	for obj in gen:
		t=obj["type"]
		if(t not in [
				"init",
				"keydown",
				"keyup",
				"keypress",
				"pointerstate"]):
			continue
		if(platform==None):
			if(t=="init"):
				platform=obj["platform"]
			else:
				raise Exception("Missing init message. Instead, the type is: "+t)
		elif(platform=="windows"):
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
					json.dump(event, sys.stdout, allow_nan=False, indent=1)
					print(file=sys.stdout, flush=True)
		elif(platform=="vnc"):
			if(obj["type"]=="output"):
				obj=obj["data"]
			t=obj["type"]
			if(t in ["keydown", "keyup", "keypress"]):
				for down in [1, 0]:
					if(t=="keypress" or t==["keydown", "keyup"][down]):
						try:
							print(" ".join([
								"Keysym",
								str(obj["vnc_client_id"])
									if "vnc_client_id" in obj else "0",
								str(down),
								str(obj["x11_keysym"])]),
								  flush=True)
						except Exception as e:
							print("Error trying to output "+t+" event: "+str(obj),file=sys.stderr)
							raise e
			elif(t=="pointerstate"):
				try:
					buttonsdown=obj["vnc_buttonsdown"]
					buttonid=1
					mask=0
					while(len(buttonsdown)>0):
						if(buttonid in buttonsdown):
							mask&=2**buttonid
							buttonsdown.remove(buttonid)
						buttonid+=1
					print(" ".join([
						"Pointer",
						str(obj["vnc_client_id"])
							if "vnc_client_id" in obj else "0",
						str(obj["vnc_xpos"]),
						str(obj["vnc_ypos"]),
						str(mask)]),
						  flush=True)
				except Exception as e:
					print("Error trying to output "+t+" event")
					raise e
		else:
			raise Exception("Unknown platform")
		yield obj

# A transformation that changes nothing while printing everything to stderr
def debug(gen):
	for obj in gen:
		print(obj, file=sys.stderr, flush=True)
		yield obj

# A transformation that changes nothing while printing everything to stderr in
# json format
def debug_json(gen):
	for obj in gen:
		json.dump(obj, sys.stderr, allow_nan=False, indent=1)
		print(file=sys.stderr, flush=True)
		yield obj

# Only has effect on windows.
# If possible, find out what keys are already down at the start of the stream,
# and release them by sending keyup events encapsulated so that no
# transformation meddles with them until the output
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
				"keyboard_hw_hash": hashobj(kb_phys)}
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
			vko=vkeyinfo(ret["win_virtualkey"])
			ret={**ret,
				"win_virtualkey_symbol": vko["win_virtualkey_symbol"],
				"win_virtualkey_description": vko["win_virtualkey_description"]}
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
							       "chord":keysdown[:i+1]}
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

# Load state from file
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
		if(state): yield {"type":"loadstate","data":state}
		for obj in gen: yield obj
	return ret

# Save state to file
def savestate(filename):
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
# macrotest is a function of a chord returning:
# - The name for the macro if the chord means save/playback
# - True if the chord means begin/cancel recording
# - False otherwise
# In normal mode, macrotest can playback or begin recording.
# While recording a macro, macrotest can cancel or save recording.
# If statekey is given, it is used to persist macros between sessions.
# ui events are generated to communicate state and state transitions.
# TRANSITION     ( FROMSTATE -> TOSTATE   )
# record         ( waiting   -> recording )
# save           ( recording -> waiting   )
# cancel         ( recording -> waiting   )
# playback       ( waiting   -> playback  )
# finishplayback ( waiting   -> playback  )
# emptyplayback  ( waiting   -> playback  )
def macro(macrotest, statekey=None):
	def ret(gen):
		macros={}
		yield {"type":"ui","data":{
			"macro.state": "waiting"}}
		for obj in gen:
			if(obj["type"]=="loadstate" and statekey and
			   statekey in obj["data"]):
				macros=obj["data"][statekey]
			mt=macrotest(obj) if obj["type"]=="chord" else False
			if(mt):
				if(mt==True):
					newmacro=[]
					yield {"type":"ui","data":{
						"macro.state": "recording",
						"macro.transition": "record"}}
					for obj in gen:
						mt2=macrotest(obj) if obj["type"]=="chord" else False
						if(mt2):
							if(mt2!=True):
								macros[mt2]=newmacro
								if(len(newmacro)==0):
									del macros[mt2]
								if(statekey):
									yield {"type":"savestate",
										"data":{statekey:macros}}
								yield {"type":"ui","data":{
									"macro.state": "waiting",
									"macro.transition": "save"}}
							else:
								yield {"type":"ui","data":{
									"macro.state": "waiting",
									"macro.transition": "cancel"}}
							break
						elif(obj["type"]=="chord"): # record only chords
							newmacro.append(obj)
						yield obj
				elif(mt in macros):
					yield {"type":"ui","data":{
						"macro.state": "playback",
						"macro.transition": "playback"}}
					yield from macros[mt]
					yield {"type":"ui","data":{
						"macro.state": "waiting",
						"macro.transition": "finishplayback"}}
				else:
					yield {"type":"ui","data":{
						"macro.state": "waiting",
						"macro.transition": "emptyplayback"}}
			else:
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
			sc=(obj["win_scancode"]
			    if "win_scancode" in obj else None)
			vk=obj["win_virtualkey"]
			t=obj["type"]
			altgr_lctrl_event={
				"type":t,
				"win_scancode": altgr_lctrl_sc,
				"win_extended": altgr_lctrl_ext,
				"win_virtualkey": lctrl}
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

def fromcsv(filename):
	return csv.reader(
		filter(lambda x:not x.startswith("#"), # Remove comments
			   open(filename)),
		lineterminator='\n',
		quotechar='"',
		quoting=0,
		delimiter=',',
		skipinitialspace=True,
		doublequote=True)

# Use the table of windows virtual keys in win_vkeys.csv to build a dictionary.
# It can be accessed through the vkeyinfo function using either a numeric or
# symbolic virtual key. It returns a dictionary with the fields win_virtualkey,
# win_virtualkey_symbol, and win_virtualkey_description.

_vkeysdict={}
for (win_virtualkey, win_virtualkey_symbol, win_virtualkey_description) in [
		(int(x,16), None if y=="" else y, z)
		for [x, y, z]
		in fromcsv("win_vkeys.csv")]:
	item={
		"win_virtualkey": win_virtualkey,
		"win_virtualkey_symbol": win_virtualkey_symbol,
		"win_virtualkey_description": win_virtualkey_description}
	if(win_virtualkey):
		_vkeysdict[win_virtualkey]=item
	if(win_virtualkey_symbol):
		_vkeysdict[win_virtualkey_symbol]=item
for vk in list(range(0x30,0x3a))+list(range(0x41,0x5b)):
	_vkeysdict[chr(vk)]=_vkeysdict[vk]

def vkeyinfo(vkey):
	try:
		return _vkeysdict[vkey]
	except KeyError:
		return {}

# Use the table of linux/vnc keysyms in keysyms.csv to build a dictionary.
# It can be accessed through the keysyminfo function using either a numeric or
# symbolic keysym. It returns a dictionary with the fields x11_keysym,
# x11_keysym_symbol, x11_keysym_description and unicode_codepoint
_keysymsdict={}
def _keysymobj_compareby(obj):
	return [
		obj["x11_keysym_description"]=="deprecated",
		obj["x11_keysym_description"].startswith("Alias for "),
		obj["x11_keysym_description"].startswith("Same as "),
		len(obj["x11_keysym_symbol"])]
for (keysym, keysym_symbol, keysym_description, unicode_codepoint) in [
		(int(n, 16), s, d, None if u=="" else int(u, 16))
		for [n, s, d, u]
		in fromcsv("keysyms.csv")]:
	item={"x11_keysym": keysym,
		  "x11_keysym_symbol": keysym_symbol,
		  "x11_keysym_description": keysym_description,
		  "unicode_codepoint": unicode_codepoint}
	save=_keysymsdict[keysym] if keysym in _keysymsdict else item
	if(_keysymobj_compareby(item) <
	   _keysymobj_compareby(save)):
		save["x11_keysym_symbol"]=item["x11_keysym_symbol"]
		save["x11_keysym_description"]=item["x11_keysym_description"]
		save["unicode_codepoint"]=item["unicode_codepoint"]
	_keysymsdict[keysym]=save
	_keysymsdict[keysym_symbol]=save

def keysyminfo(x):
	if(isinstance(x,int)):
		try: return _keysymsdict[x]
		except KeyError: pass
	if(isinstance(x,str)):
		for (prefix, replacement) in [
				("", ""),
				("XKB_KEY_", ""),
				("apXK_", "ap"),
				("SunXK_", "Sun"),
				("hpXK_", "hp"),
				("DXK_", "D"),
				("osfXK_", "osf"),
				("XF86XK_", "XF86")]:
			if(x.startswith(prefix)):
				try: return _keysymsdict[replacement+x[(len(prefix)):]]
				except KeyError: pass
	return {}

# Use the table of common names in commonname.csv to add information to
# - A new dictionary commonnamesdict
# - _keysymsdict
# - _vkeysdict

commonnamesdict={}
def add_commonname_mapping(commonname, keysym_symbol, vkey_symbol):
	item=(commonnamesdict[commonname]
		  if commonname in commonnamesdict
		  else {"commonname": commonname})
	keysym_obj=keysyminfo(keysym_symbol)
	if(keysym_obj):
		keysym_obj["commonname_obj"]=item
		if("keysym_obj" not in item):
			item["keysym_obj"]=keysym_obj
	vkey_obj=vkeyinfo(vkey_symbol)
	if(vkey_obj):
		vkey_obj["commonname_obj"]=item
		if("vkey_obj" not in item):
			item["vkey_obj"]=vkey_obj
	commonnamesdict[commonname]=item

for (commonname, keysym_symbol, vkey_symbol) in [
		(x, None if y=="" else y, None if z=="" else z)
		for [x, y, z]
		in fromcsv("commonname.csv")]:
	add_commonname_mapping(commonname, keysym_symbol, vkey_symbol)
