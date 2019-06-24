#!/usr/bin/env python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# License: See LICENSE

# This is a rather involved example, including
# - Any key functioning as both modifier and letter (events_to_chords)
# - Layout planes/layers, selectable using any number of modifiers (load, w, ch)
# - Chords transformed to other operations (chords_to_scripts)
# - Notation for key combinations, series, and repetition (scripts_to_chords)
# - Key renaming and aliasing (layout1_commonname)
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
from layout1_commonname import *
from boxdrawings import *
from time import strftime, sleep
from datetime import datetime, timedelta
from sys import argv
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
 "           S4      S3      S2             SPACE             D2      D3      D4                          " )

w("mods",
 "Bats    Sub     WM2     .       Phon    Box     .       .       .       WM2     .       .       .       " +
 "Super   Macro   WM      Nav2    Nav3    Nav4    .       Modlock Nav2    WM      Date    Super   .       " +
 "Hyper   Ctrl    Alt     Nav     Sym     Greek   Greek   Sym     Nav     Alt     Ctrl    Hyper   .       " +
 "Shell   Shift   Meta    Num     Math    Cyr     Cyr     Math    Num     Meta    Shift   Shift   .       " +
 "           Ctrl  Super     Alt            Mirror            AltGr   .       Ctrl                        " )

load("modes",[
	("X", "+X11,-Win"),
	("W", "+Win,-X11"),
	("L", "^Latex")])

#                      §1234567890+ Tqwertyuiopå Casdfghjklöä <zxcvbnm,.-^ 
ch("Sym",           """ ⁿ²³    ⁽⁾ ±  …_[]^!<>=&   \/{}*?()-:@° #$|~`+%"';  """)
ch("ShiftSym",      """              ⋀⋁⋂⋃⊂⊃¬∅⇓⇑   ≤≥≡∘  ⇐⇒⇔    ∀∃«»∈ℕℤℚℝℂ  """) # Inspired by the Knight keyboard
ch("HyperSym",      """              ⫷⫸【】  ‹›«»         ⸨⸩—         „“”‘’  """) # Inspired by http://xahlee.info/comp/unicode_matching_brackets.html
ch("Math",          """             ¬⋀⋁∈ ⇒ ≈∞∅∝   ∀∫∂ ⊂⊃ ⇔    ≤ ∃  ⇐ℕℤℚℝℂ  """)
ch("ShiftMath",     """          ≠   ⋂⋃∉ ∴ ≉       ∮  ⊏⊐      ≥ ∄  ∵∇      """)
ch("Greek",         """               ςερτυθιοπ   ασδφγηξκλ´   ζχψωβνμ     """)
ch("ShiftGreek",    """               ¨ΕΡΤΥΘΙΟΠ   ΑΣΔΦΓΗΞΚΛ    ΖΧΨΩΒΝΜ     """)
ch("Cyr",           """              йцукенгшщзхъ фывапролджэ  ячсмитьбю   """)
ch("ShiftCyr",      """              ЙЦУКЕНГШЩЗХЪ ФЫВАПРОЛДЖЭ  ЯЧСМИТЬБЮ   """)
ch("Bats",          """ ♭♮♯♩♪♫♬      ☠☢✗✆☎        ✧✦✓➔◢◣◇◆●        ◥◤      """)
ch("ShiftBats",     """                                                    """)
ch("Sub",           """        ₍₎₌₊        ₇₈₉          ₄₅₆ₓ         ₁₂₃₋  """)

load("Sym", [("0","space"),
             ("Z2","begin_unicode_input")])
load("Sub",[("SPACE","₀")])

w("Nav",
 ".       .       .       C-S-Tab C-Tab   .       .       .       10*Up   .       .       .       .       " +
 ".       Esc     Alt-F4  C-PgUp  C-PgDn  A-Home  .       Home    Up      End     Back    Del     .       " +
 ".       A-Left  A-Right S-Tab   Tab     C-Ret   .       Left    Down    Right   Ret     Ret,Up,End .    " +
 ".       .       .       .       .       .       .       Ins     10*Down S-home,Back S-end,del . .       " +
 "           .       .       .              SPACE          SPACE,left .       .                           " )

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
 "           .       .       .              SPACE             .       .       .                           " )

load("WM",[
	("Q", "A-sp,Wait-250,X"),
	("M4","A-sp,Wait-250,N")])

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

w("Phon",
 ".       .       .       .        .        .       .         .        .       .       .           .            .           " +
 ".       .quebec .whisky .echo    .romeo   .tango  .yankee   .uniform .india  .oscar  .papa       .alpha-oscar .           " +
 ".       .alfa   .sierra .delta   .foxtrot .golf   .hotel    .juliett .kilo   .lima   .oscar-echo .alpha-echo  .           " +
 ".       .zulu   .x-ray  .charlie .victor  .bravo  .november .mike    .       .       .           .            .           " )

w("Latex-Greek", # lower-case greek letters for latex
	""".          .          .          .          .          .          .          .          .          .          .          .          .  """ +
	""".          .         .\\varsigma .\\epsilon .\\rho     .\\tau     .\\upsilon .\\theta   .\\iota    .\\omicron .\\pi      .          .  """ +
	""".          .\\alpha   .\\sigma   .\\delta   .\\phi     .\\gamma   .\\eta     .\\xi      .\\kappa   .\\lamda   .          .          .  """ +
	""".          .\\zeta    .\\chi     .\\psi     .\\omega   .\\beta    .\\nu      .\\mu      .          .          .          .          .  """ )
w("Latex-ShiftGreek", # upper-case greek letters for latex
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

# List and priority of mode combinations to ignore. The empty list represents
# using all modes.
modesignored=[
	set(),
	{"Win", "X11"},
	{"Latex"},
	{"Win", "X11", "Latex"}]

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
			type=obj["type"]
			if(type=="chord"):
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
			type=obj["type"]
			if(type=="chord"):
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
				else:
					yield {**obj, "lockedmods":lockedmods}
			else:
				yield obj
	return ret

def modeswitch(modeswitchset, modeswitchname):
	def ret(gen):
		modes=set()
		for obj in gen:
			type=obj["type"]
			if(type=="init"):
				modes.add({"windows": "Win", "VNC": "X11"}[obj["platform"]])
				yield {"type":"ui","data":{"modes": modes}}
			if(type=="chord"):
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
				else:
					yield {**obj, "modes": modes}
			else:
				yield obj
	return ret

# Generate a stream of (effectivemods, planename) tuples. Note that this
# generator is not part of the pipeline, but repeatedly created and consumed by
# chords_to_scripts
def modifier_sets(downmods, lockedmods, modes):
	# depends on global variables nativemods, planeprefixes and modesignored
	#
	# First, establish a list of mode prefixes
	modeprefixes=[]
	for mignore in modesignored:
		effectivemodes=modes.difference(mignore)
		modeprefix=(
			("".join(sorted(effectivemodes))+"-")
			if len(effectivemodes)>0 else "")
		if(modeprefix not in modeprefixes):
			modeprefixes.append(modeprefix)
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
			for modeprefix in modeprefixes:
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
			for modeprefix in modeprefixes:
				yield (effectivemods, modeprefix + planename)

def chords_to_scripts(gen):
	for obj in gen:
		type=obj["type"]
		if(type=="chord"):
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

def scripts_to_chords(gen):
	for obj in gen:
		type=obj["type"]
		if(type=="script"):
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

w("Box",
 ".       b-das=N b-das=2 b-das=3 b-das=4 .       SPACE   b-___R  b-L__R  b-L___  .       .       .       " +
 ".       b-lef=d b-dow=d b-up=d  b-rig=d b-arc=Y b-_D__  b-_D_R  b-LD_R  b-LD__  back    del     .       " +
 ".       b-lef=l b-dow=l b-up=l  b-rig=l b-arc=N b-_DU_  b-_DUR  b-LDUR  b-LDU_  ret     ret,up,end .    " +
 ".       b-lef=h b-dow=h b-up=h  b-rig=h .       b-__U_  b-__UR  b-L_UR  b-L_U_  .       .       .       " +
 "           .       .       .              SPACE             .       .       .                           " )

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
			if(activation(obj, modifier)):
				command=obj["chord"][1]
				if("=" in command):
					[var, val]=command.split("=")
					settings[var]=val
				elif(len(command)==4 and set(command)<=set("LDUR_")):
					prop="".join([
						settings["lef"] if "L" in command else "-",
						settings["dow"] if "D" in command else "-",
						settings["up"]  if "U" in command else "-",
						settings["rig"] if "R" in command else "-",
						settings["das"],
						settings["arc"]])
					boxobj=boxdrawings_bestmatch(prop)
					if(boxobj):
						yield from printstring(boxobj["char"])
				yield {"type":"ui", "data":{"boxdrawings": {**settings}}}
			else:
				yield obj
	return ret

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

def macro_ui(gen):
	macrorecording=False
	for obj in gen:
		yield obj
		type=obj["type"]
		mt=macrotest(obj) if type=="chord" else False
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
			boxobj=boxdrawings_bestmatch(prop)
			ret[y]+=(boxobj["char"] if boxobj else " ")
	return ret

def color_ui(text, color):
	return ("\033[3"+str([
		"red","green","yellow","blue","magenta","cyan","white"
		].index(color)+1)+"m"+text+"\033[0m")

def termui(gen):
	oldshow=""
	on_keyup_all={
		"planename":None,
		"scriptmods":set(),
		"script":None}
	defaultdata={
		**on_keyup_all,
		"printdate.timezone":None,
		"events_to_chords.keysdown.common_name":[],
		"lockedmods":set(),
		"modes":set(),
		"chords_to_events.keysdown.common_name":[],
		"macro.state":"waiting",
		"macro.transition":None,
		"unicode_input": None}
	olddata=defaultdata
	for obj in gen:
		type=obj["type"]
		update=False
		if(type=="ui"):
			update=True
			data={**defaultdata,
				**{key:value for (key, value)
					in {**olddata, **obj["data"]}.items()
					if value!=None}}
		if(type=="keyup_all"):
			update=True
			data={**olddata, **on_keyup_all}
		if(update):
			box=(
			 boxdrawings_ui(data['boxdrawings'])
			 if 'boxdrawings' in data else ["    "]*4)
			physical=data["events_to_chords.keysdown.common_name"]
			lockedmods=data["lockedmods"]
			modes=data["modes"]
			planename=data["planename"]
			scriptmods=data["scriptmods"]
			script=data["script"]
			virtual=data["chords_to_events.keysdown.common_name"]
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
					"finishplayback": "DONE: "+script
					}[data["macro.transition"]]
			line0=" ".join(physical)
			line1=(
				(color_ui(planename+": ","cyan")
				 if planename else "")+
				(color_ui(" ".join(sorted(scriptmods)),"yellow")+" "
				    if len(scriptmods)>0 else "")+
				(script
				 if script else ""))
			line2=(
				(color_ui(" ".join(sorted(modes))+" ", "blue")
				 if len(modes)>0 else "")+
				(color_ui(" ".join(sorted(lockedmods)),"green")+" "
				 if len(lockedmods)>0 else "")+
				(color_ui(" ".join(virtual),"white")+" "
				 if len(virtual)>0 else ""))
			line3=(
				color_ui(tzstr.ljust(7), "blue") +
				color_ui(macrostate.ljust(10), "red") +
				color_ui(unicode_input_state, "magenta"))
			show=(box[0]+" "+line0+"\n"+
			      box[1]+" "+line1+"\n"+
				  box[2]+" "+line2+"\n"+
				  box[3]+" "+line3)
			if(show!=oldshow):
				print("\033[2J\033[;H" + show, file=sys.stderr, flush=True, end='')
			oldshow=show
			olddata=data
		yield obj

def ratelimit_filter(obj):
	if(obj["type"] in ["keydown", "keypress"]
	   and "common_name" in obj
	   and obj["common_name"] in ["Up", "Down", "PgUp", "PgDn"]):
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
	if(downmods=={"Macro"} and key=="SPACE"): return True
	if("Macro" in downmods):
		return ",".join([*sorted(inmods_wo_macro),key])
	return False

macrosavefile="layout1-macros.txt"
if(len(argv)>=2):
	macrosavefile=argv[1]

list_of_transformations = [
	input,                           # libkeyboa
	releaseall_at_init,              # libkeyboa
	altgr_workaround_input,          # libkeyboa
	enrich_input,                    # libkeyboa
	add_common_name,                 # common_name
	allow_repeat("physkey"),         # libkeyboa
	unstick_keys("common_name",      # libkeyboa
		key_timeouts),
	events_to_chords("common_name"), # libkeyboa
	enrich_chord("mods", "modes"),   # Customization from this file
	modlock({"Modlock"},             # Customization from this file
		"Modlock",
		"SPACE"),
	modeswitch({"Modlock","Ctrl"},   # Customization from this file
		"Modeswitch"),
	macro_ui,                        # Customization from this file
	macro(macrotest,                 # libkeyboa
		macrosavefile),
	chords_to_scripts,               # Customization from this file
	scripts_to_chords,               # Customization from this file
	boxdrawings("b"),                # Customization from this file
	unicode_input,                   # Customization from this file
	printdate("Printdate"),          # Customization from this file
	wait("Wait"),                    # Customization from this file
	chords_to_events("common_name"), # libkeyboa
	ratelimit(30, ratelimit_filter), # libkeyboa
	resolve_common_name,             # common_name
	altgr_workaround_output,         # libkeyboa
	termui,                          # Customization from this file
	sendkey_cleanup,                 # libkeyboa
	output]                          # libkeyboa

if(__name__=="__main__"):
	keyboa_run(list_of_transformations)
