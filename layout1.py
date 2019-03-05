#!/usr/bin/env python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# License: See LICENSE

from libkeyboa import *
from layout1_commonname import *
from boxdrawings import *
from time import strftime

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
 "           S4      S3      S2             SPACE             T2      T3      T4                          " )

w("mods",
 "Bats    Sub     WM2     .       Phon    Box     .       .       .       WM2     .       .       .       " +
 "Super   .       WM      Nav2    Nav3    Nav4    .       Modlock Nav2    WM      Date    Super   .       " +
 "Hyper   Ctrl    Alt     Nav     Sym     Greek   Greek   Sym     Nav     Alt     Ctrl    Hyper   .       " +
 "Shell   Shift   Meta    Num     Math    Cyr     Cyr     Math    Num     Meta    Shift   Shift   .       " +
 "           Ctrl  Super     Alt            Mirror            AltGr   .       Ctrl                        " )

#                      §1234567890+ Tqwertyuiopå Casdfghjklöä <zxcvbnm,.-^ 
ch("Sym",           """ ⁿ²³    ⁽⁾ ±  …_[]^!<>=&   \/{}*?()-:@° #$|~`+%"';  """)
ch("ShiftSym",      """              ⋀⋁⋂⋃⊂⊃¬∅⇓⇑   ≤≥≡∘  ⇐⇒⇔    ∀∃«»∈ℕℤℚℝℂ  """) #Inspired by the Knight keyboard
ch("HyperSym",      """                【】⫷⫸«»‹›         ⸨⸩—    ⦕⦖⦓⦔ „“”‘’  """) #http://xahlee.info/comp/unicode_matching_brackets.html
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
 ".       .       .       .       .       .       .       .       10*Down S-home,Back S-end,del . .       " +
 "           .       .       .              SPACE          SPACE,left .       .                           " )

w("Nav2",
 ".       .       .       .       .       .       .       .       10*PgUp .       .       .       .       " +
 ".       .       .       C-A-lef C-A-rig .       .       C-Home  PgUp    C-End   C-Back  C-Del   .       " +
 ".       .       .       S-A-Tab A-Tab   .       .       C-Left  PgDn    C-Right S-Ret   .       .       " +
 ".       .       .       .       .       .       .       .       10*PgDn .       .       S-end,S-rig,S-del " )

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
 ".       s-1     s-2     s-3     s-4     .       .       .       A-F4    .       A-sp,N  .       .       " +
 "           S4      S3      S2             SPACE             T2      T3      T4                          " )

w("Num",
 ".       .       F12     F11     F10     .       .E      .A      .B      .C      .D      .F      .       " +
 ".       F12     F9      F8      F7      .       )       7       8       9       back    /       .       " +
 ".       F11     F6      F5      F4      ]       (       4       5       6       ret     *       .       " +
 ".       F10     F3      F2      F1      [       +       1       2       3       -       :       .       " +
 "           .       .      space             0               M3      M2     .                            " )

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

w("SuperGreek", #lower-case greek letters for latex
	""".          .          .          .          .          .          .          .          .          .          .          .          .  """ +
	""".          .         .\\varsigma .\\epsilon .\\rho     .\\tau     .\\upsilon .\\theta   .\\iota    .\\omicron .\\pi      .          .  """ +
	""".          .\\alpha   .\\sigma   .\\delta   .\\phi     .\\gamma   .\\eta     .\\xi      .\\kappa   .\\lamda   .          .          .  """ +
	""".          .\\zeta    .\\chi     .\\psi     .\\omega   .\\beta    .\\nu      .\\mu      .          .          .          .          .  """ )
w("SuperShiftGreek", #upper-case greek letters for latex
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

#List and priority of native modifier combinations allowed as prefixes to plane
#names. The empty list represents an exact match between non-native modifiers
#and plane name.
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
					break
			if(not out):
				outmods=nativemods.union(planemods)
				out=inkey
			#interprete chord string expression
			if(not isinstance(out,str) or len(out)==0):
				raise Exception("Chord expression must be non-empty string")
			if("Modlock" in outmods):
				if(out=="SPACE"):
					lockedmods=set()
				else:
					lockedmods.add(planelookup(out, "mods", out))
			else:
				for item in out.split(","):
					if(len(item)>0 and item[0]=="."):
						for char in item[1:]:
							yield {"type":"chord","chord":["."+char]}
					else:
						itemch=item.split("-")
						itemmods=itemch[:-1]
						itemkey=itemch[-1]
						sendmods=set()
						for mod in itemmods:
							if mod in modnotation:
								sendmods.add(modnotation[mod])
							else:
								sendmods.add(mod)
						repeat=1
						if("*" in itemkey and itemkey.index("*")):
							mulindex=itemkey.index("*")
							repeat=int(itemkey[:mulindex])
							itemkey=itemkey[mulindex+1:]
						for _ in range(repeat):
							yield {"type":"chord","chord":
								[*sorted(sendmods.union(outmods)), itemkey]}
		else:
			yield obj

w("Box",
 ".       B-das=N B-das=2 B-das=3 B-das=4 .       SPACE   B-___R  B-L__R  B-L___  .       .       .       " +
 ".       B-lef=d B-dow=d B-up=d  B-rig=d B-arc=Y B-_D__  B-_D_R  B-LD_R  B-LD__  back    del     .       " +
 ".       B-lef=l B-dow=l B-up=l  B-rig=l B-arc=N B-_DU_  B-_DUR  B-LDUR  B-LDU_  ret     ret,up,end .    " +
 ".       B-lef=h B-dow=h B-up=h  B-rig=h .       B-__U_  B-__UR  B-L_UR  B-L_U_  .       .       .       " +
 "           S4      S3      S2             SPACE             T2      T3      T4                          " )

def boxdrawings(gen):
	settings={
		"lef":"l",
		"dow":"l",
		"up": "l",
		"rig":"l",
		"das":"N",
		"arc":"N"}
	for obj in gen:
		if(obj["type"]=="chord"
		   and len(obj["chord"])==2
		   and obj["chord"][0]=="Boxdrawings"):
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
					yield {**obj,
						"boxsettings": settings,
						"boxobj": boxobj,
						"chord":["." + boxobj["char"]]}
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
		if(obj["type"]=="chord"
		   and len(obj["chord"])==2
		   and obj["chord"][0]=="Printdate"):
			format=obj["chord"][1]
			datestr=strftime(format.replace("_", "-"))
			for char in datestr:
				yield {**obj, "chord":["." + char]}
		else:
			yield obj

list_of_transformations = [
	input,                           # libkeyboa
	releaseall_at_init,              # libkeyboa
	altgr_workaround_input,          # libkeyboa
	enrich_input,                    # libkeyboa
	add_common_name,                 # common_name
	allow_repeat("physkey"),         # libkeyboa
	events_to_chords("common_name"), # libkeyboa
	chordmachine,                    # Customization from this file
	boxdrawings,                     # Customization from this file
	printdate,                       # Customization from this file
	chords_to_events("common_name"), # libkeyboa
	resolve_common_name,             # common_name
	altgr_workaround_output,         # libkeyboa
	sendkey_cleanup,                 # libkeyboa
	output]                          # libkeyboa

keyboa_run(list_of_transformations)
