# Requires python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# License: See LICENSE

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
 "Super   Macro   WM      Nav2    Nav3    Nav4    .       Modlock Nav2    WM      Univ    Super   .       " +
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
	("4", "-RedactUI"),
	])

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
ch("Bats",          """ ♭♮♯♩♪♫♬         ✆☎        ✧✦✓➔✗ ◇◆●                """)
ch("HyperNum",      """        ₍₎₌₊        ₇₈₉          ₄₅₆ₓ         ₁₂₃₋  """)

load("Sym", [
	("0","space"),
	("Z2","begin_unicode_input"),
	])
load("HyperNum", [
	("space","₀"),
	])

w("Nav",
 ".       .       .      C-S-LTab C-Tab   .       .       .       10*Up   .       .       .       .       " +
 ".       Esc     Alt-F4  C-PgUp  C-PgDn  A-Home  .       Home    Up      End     Back    Del     .       " +
 ".       A-Left  A-Right S-LTab  Tab     C-Ret   .       Left    Down    Right   Ret     Ret,Up,End .    " +
 ".       .       .       .       .       .       .       Ins     10*Down S-home,Back S-end,del . .       " +
 "           .       .       .              space          space,left .       .                           " )

w("Nav2",
 ".       .       .       .       .       .       .       .       10*PgUp .       .       .       .       " +
 ".       .       .       C-A-lef C-A-rig .       .       C-Home  PgUp    C-End   C-Back  C-Del   .       " +
 ".       .       .      S-A-LTab A-Tab   .       .       C-Left  PgDn    C-Right S-Ret   .       .       " +
 ".       .       .       .       .       .       .       .       10*PgDn .       S-end,S-rig,S-del .     " )

load("Nav3",[
	("I", "S-up"),
	("J", "S-left"),
	("K", "S-down"),
	("L", "S-right"),
	("O", "S-end"),
	("U", "S-home"),
	("8", "10*S-up"),
	("M2","10*S-down"),
	])

load("Nav4",[
	("I", "S-pgup"),
	("J", "S-C-left"),
	("K", "S-pgdn"),
	("L", "S-C-right"),
	("O", "S-C-end"),
	("U", "S-C-home"),
	("P2","S-C-right,S-del"),
	("P", "S-C-left,S-del"),
	])

w("WM",
 ".       .       .       .       .       .       .       .       .       .       .       .       .       " +
 ".       .       .       .       .       .       .       .       s-up    .       .       .       .       " +
 ".       .       .       .       .       .       .       s-lef   s-dow   s-rig   .       .       .       " +
 ".       s-1     s-2     s-3     s-4     .       .       .       A-F4    .       .       .       .       " +
 "           .       .       .              space             .       .       .                           " )

load("WM",[
	("Q", "A-space,Wait-250,X"),
	("M4","A-space,Wait-250,N"),
	])

for key in planes["from"]:
	if(key): load("X11-WM",[(key, "C-M-section,Wait-100,"+key)])

w("Num",
 ".       .       F12     F11     F10     .       .e      .a      .b      .c      .d      .f      .       " +
 ".       F12     F9      F8      F7      [       ]       7       8       9       back    /       .       " +
 ".       F11     F6      F5      F4      (       )       4       5       6       ret     *       .       " +
 ".       F10     F3      F2      F1      space   +       1       2       3       -       :       .       " +
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
	("D", """S-pgdn"""),
	])

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
	set(),
	]

# List and priority of mode combinations together with allowed effective mods.
# The empty set represents ignoring all modes and allowing no effective mods,
# respectively.
modespriority=[
	({"Win"},set()),
	({"X11"},{"Ctrl"}),
	({"Box"},set()),
	({"Cyr"},set()),
	({"TeX"},set()),
	(set(),nativemods),
	]

modnotation={
	"s": "Super",
	"H": "Hyper",
	"M": "Meta",
	"A": "Alt",
	"C": "Ctrl",
	"S": "Shift",
	}

def planelookup(key, plane, default=None):
	fr=planes["from"]
	pl=planes[plane] if plane in planes else []
	i=fr.index(key) if key in fr else None
	if(i!=None and i<len(pl) and pl[i]):
		return pl[i]
	return default

max_numarg_digits=4

w("Box-",
 ".       b-das=N b-das=2 b-das=3 b-das=4 .       space   b-___R  b-L__R  b-L___  .       .       .       " +
 ".       b-lef=d b-dow=d b-up=d  b-rig=d b-arc=Y b-_D__  b-_D_R  b-LD_R  b-LD__  back    del     .       " +
 ".       b-lef=l b-dow=l b-up=l  b-rig=l b-arc=N b-_DU_  b-_DUR  b-LDUR  b-LDU_  ret     ret,up,end .    " +
 ".       b-lef=h b-dow=h b-up=h  b-rig=h .       b-__U_  b-__UR  b-L_UR  b-L_U_  .       .       .       " +
 "           .       .       .              space             .       .       .                           " )

load("Univ",[
	("A", "Printdate-%y%m%d"),
	("S", "Printdate-%y%m%d%H%M%S"),
	("D", "Printdate-%Y_%m_%d"),
	("F", "Printdate-%H%M"),
	("G", "Printdate-%H:%M"),
	("J", "Printdate-TZ_decrease"),
	("K", "Printdate-TZ_increase"),
	("L", "Printdate-TZ_local"),
	])
load("X11-Univ",[
	("Y", "NONE"),            # Toggle light/dark color theme
	("U", "NONE"),            # Reset zoom
	("I", "XF86ZoomIn"),      # Zoom in
	("O", "XF86ZoomOut"),     # Zoom out
	("H", "XF86ScrollUp"),    # Scroll up
	("Z", "Undo"),            # Undo
	("X", "XF86Cut"),         # Cut
	("C", "XF86Copy"),        # Copy
	("V", "XF86Paste"),       # Paste
	("N", "XF86ScrollDown")]) # Scroll down
load("Win-Univ",[
	("Y", "NONE"),            # Toggle light/dark color theme
	("U", "C-0"),             # Reset zoom
	("I", "C-plus"),          # Zoom in
	("O", "C-minus"),         # Zoom out
	("H", "NONE"),            # Scroll up
	("Z", "C-Z"),             # Undo
	("X", "S-del"),           # Cut
	("C", "C-ins"),           # Copy
	("V", "S-ins"),           # Paste
	("N", "NONE"),            # Scroll down
	])

key_timeouts={
	"S3": 10,
	"L": 10,
	"S2": 15,
	"Q2": 5,
	}

__all__=[
	"nativemods",
	"planeprefixes",
	"modespriority",
	"modnotation",
	"planelookup",
	"max_numarg_digits",
	"key_timeouts",
	]
