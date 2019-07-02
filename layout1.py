#!/usr/bin/env python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# License: See LICENSE

# This is a rather involved example, including
# - Any key functioning as both modifier and letter (events_to_chords)
# - Layout planes/layers, selectable using any number of modifiers (load, w, ch)
# - Chords transformed to other operations (chords_to_scripts)
# - Notation for key combinations, series, and repetition (scripts_to_chords)
# - Key renaming and aliasing (using commonnamesdict)
# - Chords manipulating state (boxdrawing)
# - Output depending on time (printdate)
# - Input characters by unicode codepoint (unicode_input)
#
# Run in cmd:
#   listenkey -cel | python3 layout1.py | sendkey
#
# Or in cygwin:
#   ./listenkey -cel | ./layout1.py | ./sendkey

from libkeyboa import *
from time import strftime, sleep
from datetime import datetime, timedelta
from sys import argv, stderr
from unicodedata import name as unicodename

planes={}
def load(plane, iter):
	if(not plane in planes):
		planes[plane]=[]
	pl=planes[plane]
	for i, elem in enumerate(iter):
		if(elem):
			idx=i
			if(isinstance(elem,tuple)):
				(idx,elem)=elem
			if(isinstance(idx,str)):
				idx=planes["from"].index(idx)
			while(len(pl)<=idx):
				pl.append(None)
			pl[idx]=elem
def w(plane, string):
	load(plane,
		[word if word!="." else None
		 for word in filter(lambda x: x!='',string.split(" "))])
def ch(plane, string):
	load(plane,
		[char if char!=" " else None
		 for char in string])

w("from",
 "12      1       2       3       4       5       6       7       8       9       0       02      03      " +
 "Q2      Q       W       E       R       T       Y       U       I       O       P       P2      P3      " +
 "A2      A       S       D       F       G       H       J       K       L       L2      L3      L4      " +
 "Z2      Z       X       C       V       B       N       M       M2      M3      M4      M5      .       " +
 "           S4      S3      S2             space             D2      D3      D4                          " )

w("mods",
 ".       .       WM2     mods    .       .       .       .       .       WM2     .       .       .       " +
 "Super   Macro   WM      Nav2    Nav3    Nav4    .       Modlock Nav2    WM      Date    Super   .       " +
 "Hyper   Ctrl    Alt     Nav     Sym     Greek   Greek   Sym     Nav     Alt     Ctrl    Hyper   .       " +
 "Shell   Shift   Meta    Num     Math    Bats    Bats    Math    Num     Meta    Shift   Shift   .       " +
 "           Ctrl  Super     Alt            Mirror            AltGr   .       Ctrl                        " )

load("modes",[
	("X", "+X11,-Win"),
	("W", "+Win,-X11"),
	("T", "^TeX"),
	("C", "^Cyr,-Box"),
	("B", "^Box,-Cyr"),
	("R", "+RedactUI"),
	("4", "-RedactUI")])

#                      §1234567890+ Tqwertyuiopå Casdfghjklöä <zxcvbnm,.-^ 
ch("Sym",           """ ⁿ²³    ⁽⁾ ±  …_[]^!<>=&   \/{}*?()-:@° #$|~`+%"';  """) # Inspired by https://neo-layout.org/index_en.html Layer 3
ch("ShiftSym",      """              ⋀⋁⋂⋃⊂⊃¬∅⇓⇑   ≤≥≡∘  ⇐⇒⇔    ∀∃«»∈ℕℤℚℝℂ  """) # Inspired by the Knight keyboard
ch("HyperSym",      """              ⫷⫸【】  ‹›«»         ⸨⸩—         „“”‘’  """) # Inspired by http://xahlee.info/comp/unicode_matching_brackets.html
ch("Math",          """             ¬⋀⋁∈ ⇒ ≈∞∅∝   ∀∫∂ ⊂⊃ ⇔    ≤ ∃  ⇐ℕℤℚℝℂ  """)
ch("ShiftMath",     """          ≠   ⋂⋃∉ ∴ ≉       ∮  ⊏⊐      ≥ ∄  ∵∇      """)
ch("Greek",         """               ςερτυθιοπ   ασδφγηξκλ´   ζχψωβνμ     """)
ch("ShiftGreek",    """               ¨ΕΡΤΥΘΙΟΠ   ΑΣΔΦΓΗΞΚΛ    ΖΧΨΩΒΝΜ     """)
ch("Cyr-",          """              йцукенгшщзхъ фывапролджэ  ячсмитьбю   """)
ch("Cyr-Shift",     """              ЙЦУКЕНГШЩЗХЪ ФЫВАПРОЛДЖЭ  ЯЧСМИТЬБЮ   """)
ch("Bats",          """ ♭♮♯♩♪♫♬      ☠☢✗✆☎        ✧✦✓➔◢◣◇◆●        ◥◤      """)
ch("HyperNum",      """        ₍₎₌₊        ₇₈₉          ₄₅₆ₓ         ₁₂₃₋  """)

load("Sym", [("0","space"),
             ("Z2","begin_unicode_input")])
load("HyperNum",[("space","₀")])

w("Nav",
 ".       .       .       C-S-Tab C-Tab   .       .       .       10*Up   .       .       .       .       " +
 ".       Esc     Alt-F4  C-PgUp  C-PgDn  A-Home  .       Home    Up      End     Back    Del     .       " +
 ".       A-Left  A-Right S-Tab   Tab     C-Ret   .       Left    Down    Right   Ret     Ret,Up,End .    " +
 ".       .       .       .       .       .       .       Ins     10*Down S-home,Back S-end,del . .       " +
 "           .       .       .              space          space,left .       .                           " )

w("Nav2",
 ".       .       .       .       .       .       .       .       10*PgUp .       .       .       .       " +
 ".       .       .       C-A-lef C-A-rig .       .       C-Home  PgUp    C-End   C-Back  C-Del   .       " +
 ".       .       .       S-A-Tab A-Tab   .       .       C-Left  PgDn    C-Right S-Ret   .       .       " +
 ".       .       .       .       .       .       .       .       10*PgDn .       S-end,S-rig,S-del .     " )

load("Nav3",[
	("I", "S-up"),
	("J", "S-left"),
	("K", "S-down"),
	("L", "S-right"),
	("O", "S-end"),
	("U", "S-home"),
	("8", "10*S-up"),
	("M2","10*S-down")])

load("Nav4",[
	("I", "S-pgup"),
	("J", "S-C-left"),
	("K", "S-pgdn"),
	("L", "S-C-right"),
	("O", "S-C-end"),
	("U", "S-C-home"),
	("P2","S-C-right,S-del"),
	("P", "S-C-left,S-del")])

w("WM",
 ".       .       .       .       .       .       .       .       .       .       .       .       .       " +
 ".       .       .       .       .       .       .       .       s-up    .       .       .       .       " +
 ".       .       .       .       .       .       .       s-lef   s-dow   s-rig   .       .       .       " +
 ".       s-1     s-2     s-3     s-4     .       .       .       A-F4    .       .       .       .       " +
 "           .       .       .              space             .       .       .                           " )

load("WM",[
	("Q", "A-space,Wait-250,X"),
	("M4","A-space,Wait-250,N")])

w("Num",
 ".       .       F12     F11     F10     .       .e      .a      .b      .c      .d      .f      .       " +
 ".       F12     F9      F8      F7      .       )       7       8       9       back    /       .       " +
 ".       F11     F6      F5      F4      [       (       4       5       6       ret     *       .       " +
 ".       F10     F3      F2      F1      ]       +       1       2       3       -       :       .       " +
 "           .       .      space             0               Period  Comma  .                            " )

load("Shell",[
	("Y", """C-A,C-K,.cd "$dir3",Ret"""),
	("H", """C-A,C-K,.cd "$dir2",Ret"""),
	("N", """C-A,C-K,.cd "$dir1",Ret"""),
	("T", """C-A,C-K,.dir3="`pwd`",Ret"""),
	("G", """C-A,C-K,.dir2="`pwd`",Ret"""),
	("B", """C-A,C-K,.dir1="`pwd`",Ret"""),
	("J", """C-A,C-K,.cd ..,Ret"""),
	("L", """C-A,C-K,.cd ,tab,tab"""),
	("K", """C-A,C-K,.ls -l,Ret"""),
	("M2","""C-A,C-K,.ls -la,Ret"""),
	("I", """C-A,C-K,.clear,Ret"""),
	("O", """C-A,C-K,.cd -,Ret"""),
	("U", """C-A,C-K,.jobs,Ret"""),
	("E", """S-pgup"""),
	("D", """S-pgdn""")])

w("TeX-Greek", # lower-case greek letters for TeX
	""".          .          .          .          .          .          .          .          .          .          .          .          .  """ +
	""".          .         .\\varsigma .\\epsilon .\\rho     .\\tau     .\\upsilon .\\theta   .\\iota    .\\omicron .\\pi      .          .  """ +
	""".          .\\alpha   .\\sigma   .\\delta   .\\phi     .\\gamma   .\\eta     .\\xi      .\\kappa   .\\lamda   .          .          .  """ +
	""".          .\\zeta    .\\chi     .\\psi     .\\omega   .\\beta    .\\nu      .\\mu      .          .          .          .          .  """ )
w("TeX-ShiftGreek", # upper-case greek letters for Tex
	""".          .          .          .          .          .          .          .          .          .          .          .          .  """ +
	""".          .          .          .\\Epsilon .\\Rho     .\\Tau     .\\Upsilon .\\Theta   .\\Iota    .\\Omicron .\\Pi      .          .  """ +
	""".          .\\Alpha   .\\Sigma   .\\Delta   .\\Phi     .\\Gamma   .\\Eta     .\\Xi      .\\Kappa   .\\Lamda   .          .          .  """ +
	""".          .\\Zeta    .\\Chi     .\\Psi     .\\Omega   .\\Beta    .\\Nu      .\\Mu      .          .          .          .          .  """ )

w("Mirror",
 ".       .       .       Back    Ret     .       .       .       Ret     Back    .       .       .       " +
 "P2      P       O       I       U       Y       T       R       E       W       Q       Q2      .       " +
 "L3      L2      L       K       J       H       G       F       D       S       A       .       .       " +
 ".       M4      M3      M2      M       N       B       V       C       X       Z       Z2      .       " )

nativemods=set(["Super", "Hyper", "Meta", "Alt", "Ctrl", "Shift"])

# List and priority of native modifier combinations allowed as prefixes to plane
# names. The empty list represents an exact match between non-native modifiers
# and plane name.
planeprefixes=[
	{"Shift"},
	{"Hyper"},
	set()]

# List and priority of mode combinations together with allowed effective mods.
# The empty set represents ignoring all modes.
modespriority=[
	({"Box"},set()),
	({"Cyr"},set()),
	({"TeX"},set()),
	(set(),nativemods)]

modnotation={
	"s": "Super",
	"H": "Hyper",
	"M": "Meta",
	"A": "Alt",
	"C": "Ctrl",
	"S": "Shift"}

def planelookup(key, plane, default=None):
	fr=planes["from"]
	pl=planes[plane] if plane in planes else []
	i=fr.index(key) if key in fr else None
	if(i!=None and i<len(pl) and pl[i]):
		return pl[i]
	return default

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
					"keyasmode": keyasmode}
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
						"script": "CLEAR" if key==clearkey else keyasmod}}
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
						"script": keyasmode}}
					yield {"type":"savestate","data":{"modes":modes}}
				else:
					yield {**obj, "modes": modes}
			else:
				yield obj
	return ret

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
				"script": str(out)}}
			assert isinstance(out,str) and len(out)>0, "Script must be non-empty string"
			yield {"type": "script",
				"script": out,
				"scriptmods": outmods}
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

w("Box-",
 ".       b-das=N b-das=2 b-das=3 b-das=4 .       space   b-___R  b-L__R  b-L___  .       .       .       " +
 ".       b-lef=d b-dow=d b-up=d  b-rig=d b-arc=Y b-_D__  b-_D_R  b-LD_R  b-LD__  back    del     .       " +
 ".       b-lef=l b-dow=l b-up=l  b-rig=l b-arc=N b-_DU_  b-_DUR  b-LDUR  b-LDU_  ret     ret,up,end .    " +
 ".       b-lef=h b-dow=h b-up=h  b-rig=h .       b-__U_  b-__UR  b-L_UR  b-L_U_  .       .       .       " +
 "           .       .       .              space             .       .       .                           " )

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
			"arc":"N"}
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
						settings["arc"]])
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
							"script":charname(str)}}
						if(s!="ret"):
							yield obj
						break
				else: yield obj
				res=resolve(str)
				yield {"type":"ui","data":{
					"unicode_input": (str + " " + charname(str)).strip()}}
			yield {"type":"ui","data":{"unicode_input":None}}
		else: yield obj

load("Date",[
	("K", "Printdate-TZ_increase"),
	("J", "Printdate-TZ_decrease"),
	("Z", "Printdate-TZ_UTC"),
	("L", "Printdate-TZ_local"),
	("D", "Printdate-%Y_%m_%d"),
	("C", "Printdate-%y%m%d"),
	("T", "Printdate-%H:%M"),
	("G", "Printdate-%H%M"),
	("S", "Printdate-%y%m%d%H%M%S")])

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

@retgen
def macro_ui(gen):
	macrorecording=False
	for obj in gen:
		yield obj
		t=obj["type"]
		mt=macrotest(obj) if t=="chord" else False
		if(mt):
			yield {"type":"ui", "data":{
				"scriptmods": set(),
				"planename": "Macro",
				"script": (
					"RECORD/CANCEL"
					if mt==True else mt)}}

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
				settings["arc"]])
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

@retgen
def termui(gen):
	oldshow=""
	on_keyup_all={
		"planename":None,
		"scriptmods":set(),
		"script":None}
	defaultdata={
		**on_keyup_all,
		"printdate.timezone":None,
		"events_to_chords.keysdown.commonname":[],
		"lockedmods":set(),
		"modes":set(),
		"chords_to_events.keysdown.commonname":[],
		"macro.state":"waiting",
		"macro.transition":None,
		"unicode_input": None}
	data=defaultdata
	maxlen=0
	term_clear="\033[2J"
	term_gototopleft="\033[;H"
	# reset terminal
	print(term_clear + term_gototopleft, file=stderr, flush=True, end='')
	update=True
	for obj in gen:
		t=obj["type"]
		if(t=="ui"):
			update=True
			data={**data, **obj["data"]}
		if(t=="keyup_all"):
			update=True
			data={**data, **on_keyup_all}
		if(update and (t=="tick" or not oldshow)):
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
			virtual=data["chords_to_events.keysdown.commonname"]
			macrostate=("RECORDING" if data["macro.state"]=="recording"
				else ("PLAYBACK" if data["macro.state"]=="playback" else ""))
			tz=data["printdate.timezone"]
			tzstr="local" if tz==None else ("UTC" + (("%+i" % tz) if tz!=0 else ""))
			unicode_input_state=(
				"" if data["unicode_input"]==None else
				("0x"+data["unicode_input"]))
			if(planename=="Macro"):
				script={
					"record": "RECORD",
					"cancel": "CANCEL",
					"save": "SAVE: "+script,
					"playback": "PLAYBACK: "+script,
					"finishplayback": "DONE: "+script,
					"emptyplayback": "EMPTY MACRO SLOT: "+script,
					}[data["macro.transition"]]
			line0=box[0]+" ".join(physical)
			line1=(box[1]+
				(color_ui(planename+": ","cyan")
				 if planename else "")+
				(color_ui(" ".join(sorted(scriptmods)),"yellow")+" "
				    if len(scriptmods)>0 else "")+
				(script
				 if script else ""))
			line2=(box[2]+
				(color_ui(" ".join(sorted(modes))+" ", "blue")
				 if len(modes)>0 else "")+
				(color_ui(" ".join(sorted(lockedmods)),"green")+" "
				 if len(lockedmods)>0 else "")+
				(color_ui(" ".join(virtual),"white")+" "
				 if len(virtual)>0 else ""))
			line3=(box[3]+
				color_ui(tzstr.ljust(7), "blue") +
				color_ui(macrostate.ljust(10), "red") +
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
				print(term_gototopleft + show, file=stderr, flush=True, end='')
			oldshow=show
		yield obj

def ratelimit_filter(obj):
	if(obj["type"] in ["keydown", "keypress"]
	   and "commonname" in obj
	   and obj["commonname"] in ["Up", "Down", "PgUp", "PgDn"]):
			return True
	return False

key_timeouts={
	"S3": 10,
	"L": 10,
	"S2": 15,
	"Q2": 5}

# macrotest is a function of a chord returning:
# - The name for the macro if the chord means save/playback
# - True if the chord means begin/cancel recording
# - False otherwise
def macrotest(obj):
	inchord=obj["chord"]
	inmods=set(inchord[:-1])
	inmods_wo_macro=filter(
		lambda key: planelookup(key, "mods", key)!="Macro",
		inmods)
	downmods=obj["downmods"]
	key=inchord[-1]
	if(downmods=={"Macro"} and key=="space"): return True
	if("Macro" in downmods):
		return ",".join([*sorted(inmods_wo_macro),key])
	return False

statesavefile=None
if(len(argv)>=2):
	statesavefile=argv[1]

# Add custom commonname mappings
for (commonname, keysym_symbol, vkey_symbol) in [
		(cn, None if ks=="" else ks, None if vk=="" else vk)
		for [cn, ks, vk]
		in data.fromcsv("layout1_commonname.csv", __file__)]:
	data.add_commonname_mapping(commonname, keysym_symbol, vkey_symbol)
for cn in ("A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,"+
           "F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,"+
           "Up,Down,Lef,Left,Rig,Right,"+
           "Super,Hyper,Meta,Alt,Ctrl,Shift,AltGr,"+
           "Ins,Del,Home,End,PgUp,PgDn,"+
           "Esc,Back,Tab,Ret,Comma,Period"
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

list_of_transformations = [
	tr.keyboa_input(),                                      # libkeyboa
	tr.releaseall_at_init(),                                # libkeyboa
	tr.altgr_workaround_input(),                            # libkeyboa
	tr.loadstate(statesavefile),                            # libkeyboa
	tr.add_commonname(),                                    # libkeyboa
	tr.allow_repeat("physkey"),                             # libkeyboa
	tr.unstick_keys("commonname", key_timeouts),            # libkeyboa
	tr.events_to_chords("commonname"),                      # libkeyboa
	enrich_chord("mods", "modes"),                          # layout1
	modlock({"Modlock"}, "Modlock", "space"),               # layout1
	modeswitch({"Modlock","Ctrl"}, "Modeswitch"),           # layout1
	macro_ui(),                                             # layout1
	tr.macro(macrotest, "macros"),                          # libkeyboa
	chords_to_scripts(),                                    # layout1
	scripts_to_chords(),                                    # layout1
	boxdrawings("b"),                                       # layout1
	unicode_input(),                                        # layout1
	printdate("Printdate"),                                 # layout1
	wait("Wait"),                                           # layout1
	tr.chords_to_events("commonname"),                      # libkeyboa
	tr.ratelimit(40, ratelimit_filter),                     # libkeyboa
	tr.resolve_commonname(),                                # libkeyboa
	resolve_characters(),                                   # layout1
	tr.altgr_workaround_output(),                           # libkeyboa
	termui(),                                               # layout1
	tr.savestate(statesavefile),                            # libkeyboa
	tr.keyboa_output()]                                     # libkeyboa

if(__name__=="__main__"):
	keyboa_run(list_of_transformations)
