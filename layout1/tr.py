# Requires python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# Legal: See COPYING.txt

from layout1.config import *
from libkeyboa import *
from time import strftime, sleep
from datetime import datetime, timedelta
from unicodedata import name as unicodename
import sys

@retgen
def exit_on_escape(gen):
	for obj in gen:
		yield obj
		if(obj["type"]=="keyup" and
		   (("x11_keysym" in obj and obj["x11_keysym"]==0xff1b) or
			("win_virtualkey" in obj and obj["win_virtualkey"]==0x1b))):
			yield {"type":"exit"}
			break

def enrich_chord(modifierplane, modeplane):
	def ret(gen):
		for obj in gen:
			t=obj["type"]
			if(t=="chord"):
				inchord=obj["chord"]
				inmods=set(inchord[:-1])
				key=inchord[-1]
				keyasmod=planelookup(key, modifierplane, key)
				keyasmode=planelookup(key, modeplane, key)
				downmods=set()
				for mod in inmods:
					mod=planelookup(mod, modifierplane, mod)
					downmods.add(mod)
				info={
					"key": key,
					"downmods": downmods,
					"keyasmod": keyasmod,
					"keyasmode": keyasmode,
					}
				yield {"type":"ui","data":info}
				yield {**obj, **info}
			else:
				yield obj
	return ret

def modlock(modlockset, modlockname, clearkey):
	def ret(gen):
		lockedmods=set()
		for obj in gen:
			t=obj["type"]
			if(t=="loadstate" and "lockedmods" in obj["data"]):
				lockedmods=obj["data"]["lockedmods"]
				yield {"type":"ui","data":{"lockedmods":lockedmods}}
			if(t=="chord"):
				downmods=obj["downmods"]
				key=obj["key"]
				keyasmod=obj["keyasmod"]
				if(modlockset==downmods):
					if(key==clearkey):
						lockedmods=set()
					else:
						lockedmods.add(keyasmod)
					yield {"type":"ui","data":{
						"lockedmods":lockedmods,
						"scriptmods": set(),
						"planename": modlockname,
						"script": "CLEAR" if key==clearkey else keyasmod,
						}}
					yield {"type":"savestate","data":{"lockedmods":lockedmods}}
				else:
					yield {**obj, "lockedmods":lockedmods}
			else:
				yield obj
	return ret

def modeswitch(modeswitchset, modeswitchname):
	def ret(gen):
		modes=set()
		for obj in gen:
			t=obj["type"]
			if(t=="loadstate" and "modes" in obj["data"]):
				modes=obj["data"]["modes"]
			if(t in ["loadstate","init"]):
				yield {"type":"ui","data":{"modes": modes}}
			if(t=="chord"):
				downmods=obj["downmods"]
				keyasmode=obj["keyasmode"]
				if(modeswitchset==downmods and keyasmode):
					for cmd in keyasmode.split(","):
						pm=cmd[0]
						mode=cmd[1:]
						if(pm=="^"):
							pm="-" if mode in modes else "+"
						if(pm=="+"):
							modes=modes.union({mode})
						if(pm=="-"):
							modes=modes.difference({mode})
					yield {"type":"ui","data":{
						"modes": modes,
						"scriptmods": set(),
						"planename": modeswitchname,
						"script": keyasmode,
						}}
					yield {"type":"savestate","data":{"modes":modes}}
				else:
					yield {**obj, "modes": modes}
			else:
				yield obj
	return ret

# Classify an event for the repeat functionality.
# Returns
# - A string containing a digit if the event designates a digit argument
# - "back" if the event designates erasing a digit
# - True if the event is subject to repetition
# - False otherwise
def numarg_multiplier_filter(obj):
	if(obj["type"]!="chord"): return False
	if("multiplier_ignore" in obj and obj["multiplier_ignore"]): return False
	if(obj["downmods"]!={"Meta", "Num"}): return True
	maybedigit=planelookup(obj["key"], "Num")
	if(maybedigit in {"back","0","1","2","3","4","5","6","7","8","9"}):
		return maybedigit
	return True

# Repeat functionality
@retgen
def numarg_multiplier(gen):
	numarg=""
	needs_ui_reset=False
	for obj in gen:
		r=numarg_multiplier_filter(obj)
		if(r==False): yield obj
		elif(r==True):
			if(numarg):
				repeat=int(numarg)
				yield {"type":"ui","data":{
					"multiplier":"",
					"multiplier_executing":numarg,
					}}
				for _ in range(repeat):
					yield obj
				numarg=""
				needs_ui_reset=True
			else:
				if(needs_ui_reset):
					yield {"type":"ui","data":{
						"multiplier_executing":""}}
				yield obj
		elif(r=="back"):
			numarg=numarg[:-1]
			yield {"type":"ui","data":{
				"multiplier":numarg}}
		else:
			numarg+=r
			numarg=numarg[-max_numarg_digits:]
			yield {"type":"ui","data":{
				"multiplier":numarg}}

# Generate a stream of (effectivemods, planename) tuples. Note that this
# generator is not part of the pipeline, but repeatedly created and consumed by
# chords_to_scripts
def modifier_sets(downmods, lockedmods, modes):
	# depends on global variables nativemods, planeprefixes and modespriority
	#
	# First, establish a list of mode prefixes
	modeprefixes=[]
	for (effectivemodes, allowedeffectivemods) in modespriority:
		modeprefix=(
			("".join(sorted(effectivemodes))+"-")
			if len(effectivemodes)>0 else "")
		if(effectivemodes<=modes and modeprefix not in modeprefixes):
			modeprefixes.append((modeprefix, allowedeffectivemods))
	# Loop through native modifier sets allowed as prefixes to plane name
	for planeprefix in planeprefixes:
		# For every planeprefix, there are two possible ways to find plane and
		# effective modifiers.
		downplanemods=downmods.difference(nativemods)
		downnativemods=downmods.intersection(nativemods)
		lockedplanemods=lockedmods.difference(nativemods)
		lockednativemods=lockedmods.intersection(nativemods)

		# 1) locked plane
		#   - All plane and locked mods are used to select plane.
		#   - All downnativemods are used to select plane unless also in lockednativemods.
		#   - All downnativemods not used to select plane, are in effect.
		if(planeprefix == lockednativemods.union(downnativemods)):
			planename = (
				"".join(sorted(planeprefix)) +
				"".join(sorted(lockedplanemods.union(downplanemods))))
			effectivemods = downnativemods.intersection(lockednativemods)
			for (modeprefix, allowedeffectivemods) in modeprefixes:
				if(effectivemods<=allowedeffectivemods):
					yield (effectivemods, modeprefix + planename)

		# 2) explicit plane
		#   - All downplanemods are used to select plane.
		#   - All downnativemods necessary are used to select plane.
		#   - All downnativemods not used to select plane, are in effect.
		#   - All lockedmods are rendered ineffective.
		if(planeprefix <= downnativemods):
			planename = (
				"".join(sorted(planeprefix)) +
				"".join(sorted(downplanemods)))
			effectivemods = downnativemods.difference(planeprefix)
			for (modeprefix, allowedeffectivemods) in modeprefixes:
				if(effectivemods<=allowedeffectivemods):
					yield (effectivemods, modeprefix + planename)

@retgen
def chords_to_scripts(gen):
	for obj in gen:
		t=obj["type"]
		if(t=="chord"):
			lockedmods=obj["lockedmods"]
			modes=obj["modes"]
			downmods=obj["downmods"]
			inkey=obj["key"]
			outmods=set()
			out=None
			for (outmods_candidate, planename_candidate) in \
			     modifier_sets(downmods, lockedmods, modes):
				out_candidate=planelookup(inkey, planename_candidate, None)
				if(out_candidate):
					outmods=outmods_candidate
					planename=planename_candidate
					out=out_candidate
					break
			if(not out):
				outmods=downmods
				planename=None
				out=inkey
			yield {"type":"ui","data":{
				"scriptmods": outmods,
				"planename": planename,
				"script": str(out),
				}}
			assert isinstance(out,str) and len(out)>0, "Script must be non-empty string"
			yield {"type": "script",
				"script": out,
				"scriptmods": outmods,
				}
		else:
			yield obj

@retgen
def scripts_to_chords(gen):
	for obj in gen:
		t=obj["type"]
		if(t=="script"):
			script=obj["script"]
			scriptmods=obj["scriptmods"]
			for item in script.split(","):
				if(len(item)>0 and item[0]=="."):
					for char in item[1:]:
						yield {"type":"chord","chord":["."+char]}
				elif(item in "*-"):
					yield {"type":"chord","chord":["."+item]}
				else:
					repeat=1
					if("*" in item):
						mulindex=item.index("*")
						repeat=int(item[:mulindex])
						item=item[mulindex+1:]
					itemch=item.split("-")
					itemmods=itemch[:-1]
					itemkey=itemch[-1]
					sendmods=set()
					for mod in itemmods:
						if mod in modnotation:
							sendmods.add(modnotation[mod])
						else:
							sendmods.add(mod)
					for _ in range(repeat):
						yield {"type":"chord","chord":
							[*sorted(sendmods.union(scriptmods)), itemkey]}
		else:
			yield obj

def printstring(str):
	for char in str:
		yield {"type": "keypress", "unicode_codepoint": ord(char)}

def activation(obj, modifier):
	return (
		obj["type"]=="chord"
		and len(obj["chord"])==2
		and (obj["chord"][0]==modifier or
		     ("downmods" in obj and obj["downmods"]=={modifier})))

def boxdrawings(modifier):
	def ret(gen):
		settings={
			"lef":"l",
			"dow":"l",
			"up": "l",
			"rig":"l",
			"das":"N",
			"arc":"N",
			}
		yield {"type":"ui", "data":{"boxdrawings": {**settings}}}
		for obj in gen:
			if(obj["type"]=="loadstate" and "boxdrawing_state" in obj["data"]):
				settings=obj["data"]["boxdrawing_state"]
				yield {"type":"ui", "data":{"boxdrawings": {**settings}}}
			if(activation(obj, modifier)):
				command=obj["chord"][1]
				if("=" in command):
					[var, val]=command.split("=")
					settings[var]=val
					yield {"type":"ui", "data":{"boxdrawings": {**settings}}}
					yield {
						"type":"savestate",
						"data":{"boxdrawing_state":settings}}
				elif(len(command)==4 and set(command)<=set("LDUR_")):
					prop="".join([
						settings["lef"] if "L" in command else "-",
						settings["dow"] if "D" in command else "-",
						settings["up"]  if "U" in command else "-",
						settings["rig"] if "R" in command else "-",
						settings["das"],
						settings["arc"],
						])
					boxobj=data.boxdrawings_bestmatch(prop)
					if(boxobj):
						yield from printstring(boxobj["char"])
			else:
				yield obj
	return ret

@retgen
def unicode_input(gen):
	def resolve(str):
		if(str=="" or len(str)>6): return ""
		try: return chr(int(str,16))
		except ValueError: return ""
	def charname(str):
		try: return unicodename(resolve(str))
		except ValueError: return ""
		except TypeError: return ""
	for obj in gen:
		if(obj["type"]=="chord" and obj["chord"]==["begin_unicode_input"]):
			str=""
			yield {"type":"ui","data":{"unicode_input":str}}
			hexchars="0123456789abcdef"
			for obj in gen:
				if(obj["type"]=="chord" and len(obj["chord"])==1):
					s=obj["chord"][0].lower()
					if(s in hexchars):
						str+=s
					elif(len(s)==2 and s[1] in hexchars):
						str+=s[1]
					elif(s=="back"):
						str=str[:-1]
					elif(s=="esc"):
						break
					else:
						yield from printstring(resolve(str))
						yield {"type":"ui","data":{
							"planename":"Unicode",
							"script":charname(str),
							}}
						if(s!="ret"):
							yield obj
						break
				else: yield obj
				res=resolve(str)
				yield {"type":"ui","data":{
					"unicode_input": (str + " " + charname(str)).strip()}}
			yield {"type":"ui","data":{"unicode_input":None}}
		else: yield obj

def printdate(modifier):
	def ret(gen):
		TZ=None
		for obj in gen:
			if(obj["type"]=="loadstate" and "timezone" in obj["data"]):
				TZ=obj["data"]["timezone"]
				yield {"type":"ui","data":{"printdate.timezone":TZ}}
			if(activation(obj, modifier)):
				command_or_format=obj["chord"][1]
				if("%" in command_or_format):
					format=command_or_format
					datestr=strftime(format.replace("_", "-"),
						(datetime.now().timetuple())
						if TZ==None else
						((datetime.utcnow()+timedelta(hours=TZ)).timetuple()))
					yield from printstring(datestr)
				else:
					command=command_or_format
					if(command=="TZ_increase"):
						TZ=min((TZ or 0)+1, 12)
					elif(command=="TZ_decrease"):
						TZ=max((TZ or 0)-1, -12)
					elif(command=="TZ_UTC"):
						TZ=0
					elif(command=="TZ_local"):
						TZ=None
					yield {"type":"ui","data":{"printdate.timezone":TZ}}
					yield {"type":"savestate","data":{"timezone":TZ}}
			else:
				yield obj
	return ret

def compose(prefix):
	def ret(gen):
		def objs(buf):
			for scr in buf:
				yield {"type": "script", "script": scr, "scriptmods":set()}
		for obj in gen:
			if(obj["type"]=="script" and
			   obj["scriptmods"]==set() and
			   obj["script"].startswith(prefix)):
				buf=(obj["script"][len(prefix):],)
				for obj in gen:
					if(obj["type"]=="script"):
						scr=obj["script"]
						isspace=scr in {"space","sp"}
						if(len(obj["scriptmods"])>0 or
						   isspace):
							yield from objs(buf)
							if(not isspace):
								yield obj
							break
						if(scr.startswith(prefix)):
							scr=scr[len(prefix):]
						buf=(*buf, scr)
						if(buf in composition):
							buf=(composition[buf],)
						f=lambda x:x[:len(buf)]==buf and len(buf)<len(x)
						if(len(list(filter(f, composition.keys())))==0):
							yield from objs(buf)
							break
					else: yield obj
			else: yield obj
	return ret

def wait(modifier):
	def ret(gen):
		for obj in gen:
			if(activation(obj, modifier)):
				milliseconds=int(obj["chord"][1])
				seconds=milliseconds/1000
				sleep(seconds)
			else:
				yield obj
	return ret

def boxdrawings_ui(settings):
	ret=["","","",""]
	for y in range(4):
		for x in range(4):
			prop="".join([
				settings["lef"] if x in [2,3] else "-",
				settings["dow"] if y in [1,2] else "-",
				settings["up"]  if y in [2,3] else "-",
				settings["rig"] if x in [1,2] else "-",
				settings["das"],
				settings["arc"],
				])
			boxobj=data.boxdrawings_bestmatch(prop)
			ret[y]+=(boxobj["char"] if boxobj else " ")
	return ret

# Class for terminal text that keeps track of rendered length
class Tt():
	def __init__(self, txt="", txtlen=None):
		self.txt=txt
		self.len=len(txt) if txtlen==None else txtlen
	def __add__(self, other):
		return ((self+Tt(other)) if isinstance(other,str) else
			Tt(self.txt+other.txt,self.len+other.len))
	def __str__(self): return self.txt
	def __len__(self): return self.len

# Colored terminal text.
def color_ui(text, color):
	return Tt(("\033[3"+str([
		"red","green","yellow","blue","magenta","cyan","white"
		].index(color)+1)+"m"+text+"\033[0m"),
		len(text))

# This is the TUI (text user interface). It works in most terminals on both
# windows and linux. It is rather ugly code because it depends on almost
# everything else, but in doing so it saves a lot of other things from being
# interdependent.
def termui(file=sys.stderr):
	def ret(gen):
		oldshow=""
		on_keyup_all={
			"planename":None,
			"scriptmods":set(),
			"script":None,
			"multiplier_executing":"",
			}
		defaultdata={
			**on_keyup_all,
			"printdate.timezone":None,
			"events_to_chords.keysdown.commonname":[],
			"lockedmods":set(),
			"modes":set(),
			"multiplier":"",
			"chords_to_events.keysdown.commonname":[],
			"macro.state":"waiting",
			"macro.transition":"finishplayback",
			"macro.key":"",
			"unicode_input": None,
			}
		script_newer_than_macro_transition=True
		data=defaultdata
		maxlen=0
		term_clear="\033[2J"
		term_gototopleft="\033[;H"
		# reset terminal
		print(term_clear + term_gototopleft, file=file, flush=True, end='')
		update=True
		for obj in gen:
			t=obj["type"]
			if(t=="ui"):
				update=True
				data={**data, **obj["data"]}
				if("macro.transition" in obj["data"]):
					script_newer_than_macro_transition=False
				if("script" in obj["data"]):
					script_newer_than_macro_transition=True
			if(t=="keyup_all"):
				update=True
				data={**data, **on_keyup_all}
				script_newer_than_macro_transition=True
			if(update):
				update=False
				modes=data["modes"]
				box=[Tt(x+" ") for x in (
				 boxdrawings_ui(data["boxdrawings"])
				 if ("boxdrawings" in data and "Box" in modes) else [""]*4)]
				physical=data["events_to_chords.keysdown.commonname"]
				lockedmods=data["lockedmods"]
				planename=data["planename"]
				scriptmods=data["scriptmods"]
				script=data["script"]
				multiplier=(data["multiplier"]+"×"
					if data["multiplier"] else "")
				multiplier_executing=(str(int(data["multiplier_executing"]))+"×"
					if data["multiplier_executing"] else "")
				virtual=data["chords_to_events.keysdown.commonname"]
				tz=data["printdate.timezone"]
				tzstr="local" if tz==None else ("UTC" + (("%+i" % tz) if tz!=0 else ""))
				unicode_input_state=(
					"" if data["unicode_input"]==None else
					("0x"+data["unicode_input"]))
				mk=data["macro.key"]
				mt=data["macro.transition"]
				macro_script_prefix={
					"record": "RECORDING",
					"cancel": "CANCEL",
					"save": "SAVE: "+mk,
					"playback": "PLAY: "+mk,
					"finishplayback": "DONE: "+mk,
					"emptyplayback": "NONE: "+mk,
					}[mt]
				macro_color=("green" if mt in ["save", "finishplayback"] else "red")
				if(mt not in ["playback", "record"] and
				   script_newer_than_macro_transition):
					macro_script_prefix=""
				if(mt!="finishplayback" and
				   not script_newer_than_macro_transition):
					planename=""
					script=""
				mult_exec_ui=(
					color_ui(multiplier_executing, "yellow")+" "
					if multiplier_executing else "")
				mult_exec_before_macro=(
					mt in ["playback", "finishplayback", "emptyplayback"] and
					macro_script_prefix)
				line0=box[0]+" ".join(physical)
				line1=(box[1]+
					(mult_exec_ui if mult_exec_before_macro else "")+
					(color_ui(macro_script_prefix, macro_color)+" "
					 if macro_script_prefix else "")+
					(color_ui(planename+": ","cyan")
					 if planename else "")+
					(color_ui(" ".join(sorted(scriptmods)),"yellow")+" "
					 if len(scriptmods)>0 else "")+
					(mult_exec_ui if not mult_exec_before_macro else "")+
					(script
					 if script else ""))
				line2=(box[2]+
					(color_ui(" ".join(sorted(modes))+" ", "blue")
					 if len(modes)>0 else "")+
					(color_ui(" ".join(sorted(lockedmods)),"green")+" "
					 if len(lockedmods)>0 else "")+
					(color_ui(multiplier.rjust(max_numarg_digits+1), "yellow")+" ")+
					(color_ui(" ".join(virtual),"white")+" "
					 if len(virtual)>0 else ""))
				line3=(box[3]+
					color_ui(tzstr.ljust(7), "blue") +
					color_ui(unicode_input_state, "magenta"))
				showarr=[line0,line1,line2,line3]
				if("RedactUI" in modes):
					showarr=[Tt()]*4
					showarr[1]=color_ui(" ***", "blue")
				# If previous lines were very long
				if(maxlen>80):
					# then begin by clearing
					show=term_clear
					# and reset the historical maximum line length
					maxlen=0
				else:
					show=""
				# Calculate historical maximum of rendered length of lines
				maxlen=max(maxlen,max(map(len,showarr)))
				# Extend every line with spaces to that length and covert to string
				showarr=[str(x)+" "*(maxlen-len(x)) for x in showarr]
				show+="\n".join(showarr)
				if(show!=oldshow):
					# In order to avoid blinking, first move to top-left corner of
					# terminal without clearing, then overwrite.
					print(term_gototopleft + show, file=file, flush=True, end='')
				oldshow=show
			yield obj
	return ret

# Colored stumpwm text.
def color_stumpwmui(text, color):
	return (({
		"red":"^1*",
		"green":"^2*",
		"yellow":"^3*",
		"blue":"^4*",
		"magenta":"^5*",
		"cyan":"^6*",
		"white":"^7*",
		"brightred":"^B^1*",
		"brightgreen":"^B^2*",
		"brightyellow":"^B^3*",
		"brightblue":"^B^4*",
		"brightmagenta":"^B^5*",
		"brightcyan":"^B^6*",
		"brightwhite":"^B^7*",
		})[color]+(text.replace("^","^^"))+"^**")

# Similar to termui but will instead output one line of text suitable for
# rendering in stumpwm. No-op if file is None.
def stumpwmui(file=None):
	if(file==None):
		def ret(gen):
			for obj in gen:
				yield obj
		return ret
	def ret(gen):
		oldoutput=""
		on_keyup_all={
			"multiplier_executing":"",
			}
		defaultdata={
			**on_keyup_all,
			"printdate.timezone":None,
			"events_to_chords.keysdown.commonname":[],
			"lockedmods":set(),
			"modes":set(),
			"multiplier":"",
			"chords_to_events.keysdown.commonname":[],
			"macro.state":"waiting",
			"macro.transition":"finishplayback",
			"macro.key":"",
			"unicode_input": None,
			}
		script_newer_than_macro_transition=True
		data=defaultdata
		update=True
		for obj in gen:
			t=obj["type"]
			if(t=="ui"):
				update=True
				data={**data, **obj["data"]}
				if("macro.transition" in obj["data"]):
					script_newer_than_macro_transition=False
				if("script" in obj["data"]):
					script_newer_than_macro_transition=True
			if(t=="keyup_all"):
				update=True
				data={**data, **on_keyup_all}
				script_newer_than_macro_transition=True
			if(update):
				update=False
				modes=data["modes"]

				# Build output
				output=[]
				# Magenta unicode input
				if data["unicode_input"]!=None:
					output.append(color_stumpwmui("0x"+data["unicode_input"], "magenta"))
				# Right align
				output.append("^>")
				# Numerical argument
				if(data["multiplier"]):
					output.append(color_stumpwmui((data["multiplier"]+"×").rjust(max_numarg_digits+1), "yellow"))
				# Macro stuff
				mk=data["macro.key"]
				mt=data["macro.transition"]
				if(mt in ["playback", "record"] or not script_newer_than_macro_transition):
					multiplier_ui=(color_stumpwmui(str(int(data["multiplier_executing"]))+"×", "yellow") if data["multiplier_executing"] else "")
					macro_indicator_ui={
						"record": color_stumpwmui("RECORD","red"),
						"cancel": color_stumpwmui("CANCEL","red"),
						"save": color_stumpwmui("SAVE: "+mk,"green"),
						"playback": color_stumpwmui("PLAY: ","red")+multiplier_ui+color_stumpwmui(mk,"red"),
						"finishplayback": color_stumpwmui("DONE: ","green")+multiplier_ui+color_stumpwmui(mk,"green"),
						"emptyplayback": color_stumpwmui("NONE: "+mk,"red"),
					}[mt]
					output.append(macro_indicator_ui)
				# Locked modifiers
				output.extend([color_stumpwmui(x,"green") for x in sorted(data["lockedmods"])])
				# Box drawing status
				if("boxdrawings" in data and "Box" in modes):
					output.append(color_stumpwmui(boxdrawings_ui(data["boxdrawings"])[2],"white"))
				# Modes
				output.extend([color_stumpwmui(x,"brightblue") for x in sorted(modes)])
				# Timezone indicator
				tz=data["printdate.timezone"]
				tzstr="" if tz==None else ("UTC" + (("%+i" % tz) if tz!=0 else ""))
				output.append(color_stumpwmui(tzstr.ljust(7), "brightyellow"))

				output=" ".join(filter(lambda x:x, output))
				if("RedactUI" in modes):
					output=color_stumpwmui("***", "brightblue")
				if(output!=oldoutput):
					print(output, file=file, flush=True)
				oldoutput=output
			yield obj
	return ret

def ratelimit_filter_updown(obj):
	if(obj["type"] in ["keydown", "keypress"]
	   and "commonname" in obj
	   and obj["commonname"] in ["Up", "Down", "PgUp", "PgDn"]):
			return True
	return False

def ratelimit_filter_keyevent(obj):
	return obj["type"] in ["keypress", "keydown", "keyup"]

# macrotest(event, recording) is a function of an event and a bool indicating
# whether the current state is recording. During recording, it returns:
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
def macrotest(obj, _):
	if("macrotest" in obj):
		return obj["macrotest"]
	return [False, None]

@retgen
def macro_and_multiplier_controller(gen):
	in_recording=False
	for obj in gen:
		if(obj["type"]!="chord"):
			yield obj
			continue
		inchord=obj["chord"]
		inmods=set(inchord[:-1])
		inmods_wo_macro=filter(
			lambda key: planelookup(key, "mods", key)!="Macro",
			inmods)
		downmods=obj["downmods"]
		key=inchord[-1]
		if(downmods=={"Macro"} and key=="space"):
			yield {**obj,
				"macrotest": ["record", None],
				"multiplier_ignore": True,
				}
			in_recording=True
			continue
		if(downmods=={"Macro"} and key=="S2"):
			yield {**obj,
				"macrotest": ["cancel", None],
				"multiplier_ignore": True,
				}
			in_recording=False
			continue
		if("Macro" in downmods):
			macroname=",".join([*sorted(inmods_wo_macro),key])
			yield {**obj,
				"macrotest": [
					"save" if in_recording else "playback",
					macroname],
				"multiplier_ignore": in_recording,
				}
			in_recording=False
			continue
		if(in_recording):
			yield {**obj,
				"macrotest": ["recordable", obj],
				}
			continue
		yield obj

# Add custom commonname mappings
for (commonname, keysym_symbol, vkey_symbol) in [
		(cn, None if ks=="" else ks, None if vk=="" else vk)
		for [cn, ks, vk]
		in data.fromcsv("custom_commonname.csv", __file__)]:
	data.add_commonname_mapping(commonname, keysym_symbol, vkey_symbol)
for cn in ("A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,"+
           "F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,"+
           "Up,Down,Lef,Left,Rig,Right,"+
           "Super,Hyper,Meta,Alt,Ctrl,Shift,AltGr,"+
           "Ins,Del,Home,End,PgUp,PgDn,"+
           "Esc,Back,Tab,LTab,Ret,Comma,Period"
          ).split(","):
	data.add_commonname_alias(cn, cn.lower(), True)
	data.add_commonname_alias(cn.title(), cn.lower())

@retgen
def resolve_characters(gen):
	for obj in gen:
		if(obj["type"] in ["keydown", "keyup", "keypress"] and
		   "commonname" in obj and
		   "win_virtualkey" not in obj and
		   "x11_keysym" not in obj and
		   "unicode_codepoint" not in obj and
		   len(obj["commonname"])<=2 and
		   (obj["commonname"][0]=="." or
		    len(obj["commonname"])==1)):
			yield {**obj, "unicode_codepoint": ord(obj["commonname"][-1])}
		else:
			yield obj

__all__=[
	"exit_on_escape",
	"enrich_chord",
	"modlock",
	"modeswitch",
	"numarg_multiplier_filter",
	"numarg_multiplier",
	"modifier_sets",
	"chords_to_scripts",
	"scripts_to_chords",
	"printstring",
	"activation",
	"boxdrawings",
	"unicode_input",
	"printdate",
	"compose",
	"wait",
	"boxdrawings_ui",
	"color_ui",
	"termui",
	"ratelimit_filter_updown",
	"ratelimit_filter_keyevent",
	"macrotest",
	"macro_and_multiplier_controller",
	"resolve_characters",
	]
