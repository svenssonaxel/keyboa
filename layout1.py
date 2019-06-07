#!/usr/bin/env python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# License: See LICENSE

# This is a rather involved example, including
# - Any key functioning as both modifier and letter (chordmachine)
# - Layout planes/layers, selectable using any number of modifiers (load, w, ch)
# - Chords transformed to other chords (chordmachine)
# - Notation for key combinations, series, and repetition (chordmachine)
# - Key renaming and aliasing (layout1_commonname)
# - Chords manipulating state (boxdrawing)
# - Output depending on time (printdate)
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
 "Super   .       WM      Nav2    Nav3    Nav4    .       Modlock Nav2    WM      Date    Super   .       " +
 "Hyper   Ctrl    Alt     Nav     Sym     Greek   Greek   Sym     Nav     Alt     Ctrl    Hyper   .       " +
 "Shell   Shift   Meta    Num     Math    Cyr     Cyr     Math    Num     Meta    Shift   Shift   .       " +
 "           Ctrl  Super     Alt            Mirror            AltGr   .       Ctrl                        " )

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

load("Sym", [("0","space")])
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

w("SuperGreek", # lower-case greek letters for latex
	""".          .          .          .          .          .          .          .          .          .          .          .          .  """ +
	""".          .         .\\varsigma .\\epsilon .\\rho     .\\tau     .\\upsilon .\\theta   .\\iota    .\\omicron .\\pi      .          .  """ +
	""".          .\\alpha   .\\sigma   .\\delta   .\\phi     .\\gamma   .\\eta     .\\xi      .\\kappa   .\\lamda   .          .          .  """ +
	""".          .\\zeta    .\\chi     .\\psi     .\\omega   .\\beta    .\\nu      .\\mu      .          .          .          .          .  """ )
w("SuperShiftGreek", # upper-case greek letters for latex
	""".          .          .          .          .          .          .          .          .          .          .          .          .  """ +
	""".          .          .          .\\Epsilon .\\Rho     .\\Tau     .\\Upsilon .\\Theta   .\\Iota    .\\Omicron .\\Pi      .          .  """ +
	""".          .\\Alpha   .\\Sigma   .\\Delta   .\\Phi     .\\Gamma   .\\Eta     .\\Xi      .\\Kappa   .\\Lamda   .          .          .  """ +
	""".          .\\Zeta    .\\Chi     .\\Psi     .\\Omega   .\\Beta    .\\Nu      .\\Mu      .          .          .          .          .  """ )

w("Mirror",
 ".       .       .       Back    Ret     .       .       .       Ret     Back    .       .       .       " +
 "P2      P       O       I       U       Y       T       R       E       W       Q       Q2      .       " +
 "L3      L2      L       K       J       H       G       F       D       S       A       .       .       " +
 ".       M4      M3      M2      M       N       B       V       C       X       Z       Z2      .       " )

nativemodifiers=["Super", "Hyper", "Meta", "Alt", "Ctrl", "Shift"]

# List and priority of native modifier combinations allowed as prefixes to plane
# names. The empty list represents an exact match between non-native modifiers
# and plane name.
planeprefixes=[
	["Shift"],
	["Hyper"],
	[]]

modnotation={
	"s": "Super",
	"H": "Hyper",
	"M": "Meta",
	"A": "Alt",
	"C": "Ctrl",
	"S": "Shift",
	"B": "Boxdrawings"}

def planelookup(key, plane, default=None):
	fr=planes["from"]
	pl=planes[plane] if plane in planes else []
	i=fr.index(key) if key in fr else None
	if(i!=None and i<len(pl) and pl[i]):
		return pl[i]
	return default

def chordmachine(gen):
	lockedmods=set()
	for obj in gen:
		type=obj["type"]
		if(type=="chord"):
			inchord=obj["chord"]
			inmods=set(inchord[:-1])
			inkey=inchord[-1]
			planemods=set()
			nativemods=set()
			for mod in inmods.union(lockedmods):
				mod=planelookup(mod, "mods", mod)
				if(mod in nativemodifiers):
					nativemods.add(mod)
				else:
					planemods.add(mod)
			out=None
			outmods=set()
			planename="".join(sorted(planemods))
			for pre in planeprefixes:
				o=planelookup(inkey, "".join(pre)+planename, None)
				if(o and set(pre)<=nativemods):
					outmods=nativemods-set(pre)
					out=o
					planename="".join(pre)+planename
					break
			if(not out):
				outmods=nativemods.union(planemods)
				planename=None
				out=inkey
			yield {"type":"ui","data":{
				"chordmachine.planename": planename,
				"chordmachine.nativemods":sorted(nativemods),
				"chordmachine.planemods":sorted(planemods),
				"chordmachine.outmods":sorted(outmods),
				"chordmachine.out": str(out)}}
			# interprete chord string expression
			assert isinstance(out,str) and len(out)>0, "Chord expression must be non-empty string"
			if("Modlock" in outmods):
				if(out=="SPACE"):
					lockedmods=set()
				else:
					lockedmods.add(planelookup(out, "mods", out))
				yield {"type":"ui","data":{
					"chordmachine.lockedmods":sorted(lockedmods)}}
			else:
				for item in out.split(","):
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
								[*sorted(sendmods.union(outmods)), itemkey]}
		else:
			if(type=="keyup_all"):
				yield {"type":"ui","data":{
					"chordmachine.planename": None,
					"chordmachine.nativemods":None,
					"chordmachine.planemods":None,
					"chordmachine.outmods":None,
					"chordmachine.out": None}}
			yield obj

chorddispatches={
	#Chord modifier  type value     data key
	"Boxdrawings": ("boxdrawings", "command"),
	"Printdate":   ("printdate",   "format"),
	"Wait":        ("wait",        "ms")}

def chord_dispatch(dispatch):
	def ret(gen):
		for obj in gen:
			if(obj["type"]=="chord"
			   and len(obj["chord"])==2
			   and obj["chord"][0] in dispatch):
				[dispatchkey, data] = obj["chord"]
				(typevalue, datakey) = dispatch[dispatchkey]
				yield {"type": typevalue, datakey: data}
			else:
				yield obj
	return ret

w("Box",
 ".       B-das=N B-das=2 B-das=3 B-das=4 .       SPACE   B-___R  B-L__R  B-L___  .       .       .       " +
 ".       B-lef=d B-dow=d B-up=d  B-rig=d B-arc=Y B-_D__  B-_D_R  B-LD_R  B-LD__  back    del     .       " +
 ".       B-lef=l B-dow=l B-up=l  B-rig=l B-arc=N B-_DU_  B-_DUR  B-LDUR  B-LDU_  ret     ret,up,end .    " +
 ".       B-lef=h B-dow=h B-up=h  B-rig=h .       B-__U_  B-__UR  B-L_UR  B-L_U_  .       .       .       " +
 "           .       .       .              SPACE             .       .       .                           " )

def printstring(str):
	for char in str:
		yield {"type": "keypress", "unicode_codepoint": ord(char)}

def boxdrawings(gen):
	settings={
		"lef":"l",
		"dow":"l",
		"up": "l",
		"rig":"l",
		"das":"N",
		"arc":"N"}
	for obj in gen:
		if(obj["type"]=="boxdrawings"):
			command=obj["command"]
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

load("Date",[
	("D", "Printdate-%Y_%m_%d"),
	("C", "Printdate-%y%m%d"),
	("T", "Printdate-%H:%M"),
	("G", "Printdate-%H%M"),
	("S", "Printdate-%y%m%d%H%M%S")])

def printdate(gen):
	for obj in gen:
		if(obj["type"]=="printdate"):
			format=obj["format"]
			datestr=strftime(format.replace("_", "-"))
			yield from printstring(datestr)
		else:
			yield obj

def wait(gen):
	for obj in gen:
		if(obj["type"]=="wait"):
			milliseconds=int(obj["ms"])
			seconds=milliseconds/1000
			sleep(seconds)
		else:
			yield obj

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
	olddata={}
	defaultdata={
		"events_to_chords.keysdown.common_name":[],
		"chordmachine.lockedmods":[],
		"chordmachine.nativemods":[],
		"chordmachine.planemods":[],
		"chordmachine.outmods":[],
		"chordmachine.planename":None,
		"chordmachine.out":"",
		"chords_to_events.keysdown.common_name":[],
		"macro.recording":False,
		"macro.playback":False}
	for obj in gen:
		if(obj["type"]=="ui"):
			data={**defaultdata,
			      **{key:value for (key, value)
			         in {**olddata, **obj["data"]}.items()
			         if value!=None}}
			box=(
			 boxdrawings_ui(data['boxdrawings'])
			 if 'boxdrawings' in data else ["    "]*4)
			physical=data["events_to_chords.keysdown.common_name"]
			lockedmods=set(data["chordmachine.lockedmods"])
			nativemods=set(data["chordmachine.nativemods"])
			planemods=set(data["chordmachine.planemods"])
			outmods=set(data["chordmachine.outmods"])
			showlocked=lockedmods
			shownative=(nativemods-lockedmods)&outmods
			showplane=(planemods-lockedmods)&outmods
			planename=data["chordmachine.planename"]
			out=data["chordmachine.out"]
			virtual=data["chords_to_events.keysdown.common_name"]
			macrostate="RECORDING" if data["macro.recording"] else ("PLAYBACK" if data["macro.playback"] else "")
			show=(box[0]+" "+
			      " ".join(physical)+
				  "\n"+
			      box[1]+" "+
				  (color_ui(" ".join(sorted(showlocked)),"green")+" "
				   if len(showlocked)>0 else "")+
				  (color_ui(" ".join(sorted(shownative)),"yellow")+" "
				   if len(shownative)>0 else "")+
				  (color_ui(" ".join(sorted(showplane)),"red")+" "
				   if len(showplane)>0 else "")+
				  (color_ui(planename+": ","cyan")
				   if planename else "")+
				  out+
				  "\n"+
				  box[2]+" "+
				  (color_ui(" ".join(virtual),"blue")+" "
				   if len(virtual)>0 else "")+
				  "\n"+
				  box[3]+" "+color_ui(macrostate, "red"))
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
	macro("Q", "SPACE"),             # libkeyboa
	chordmachine,                    # Customization from this file
	chord_dispatch(chorddispatches), # Customization from this file
	chords_to_events("common_name"), # libkeyboa
	boxdrawings,                     # Customization from this file
	printdate,                       # Customization from this file
	wait,                            # Customization from this file
	ratelimit(30, ratelimit_filter), # libkeyboa
	resolve_common_name,             # common_name
	altgr_workaround_output,         # libkeyboa
	termui,                          # Customization from this file
	sendkey_cleanup,                 # libkeyboa
	output]                          # libkeyboa

keyboa_run(list_of_transformations)
