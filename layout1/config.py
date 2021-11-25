# Requires python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# Legal: See COPYING.txt

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
composition={}
def compose(composedict):
	global composition
	composition={**composition,
		**{tuple(key):composedict[key]
		   for key in composedict}}

w("from",
 "12      1       2       3       4       5       52                      62      6       7       8       9       0       02      03      " +
 "Q2      Q       W       E       R       T       T2                      Y2      Y       U       I       O       P       P2      P3      " +
 "A2      A       S       D       F       G                                       H       J       K       L       L2      L3      L4      " +
 "Z2      Z       X       C       V       B       B2                      N2      N       M       M2      M3      M4      M5      .       " +
 "S5      S4      S3      S2                                                              D1      D2      D3      D4                      " +
 "                                                SC1     SC2     DC2     DC1                                                             " +
 "                                                        SC3     DC3                                                                     " +
 "                                        back    del     SC4     DC4     ret     space                                                   " )

w("mods",
 ".       .       .       mods    .       .       .                       .       .       .       .       .       .       .       .       " +
 "Super   Macro   WM      Nav2    Nav3    Nav4    .                       .       .       Modlock Nav2    WM      Univ    Super   .       " +
 "Hyper   Ctrl    Alt     Nav     Sym     Greek                                   Greek   Sym     Nav     Alt     Ctrl    Hyper   .       " +
 "Shell   Shift   Meta    Num     Math    Bats    .                       .       Bats    Math    Num     Meta    Shift   Shift   .       " +
 ".       Ctrl    Super   Alt                                                             AltGr   .       Ctrl    .                       " +
 "                                                .       .       .       .                                                               " +
 "                                                        .       .                                                                       " +
 "                                        .       .       .       .       .       Mirror                                                  " )

load("modes",[
	("X", "+X11,-Win"),
	("W", "+Win,-X11"),
	("T", "^TeX"),
	("C", "^Cyr,-Box"),
	("B", "^Box,-Cyr"),
	("R", "+RedactUI"),
	("4", "-RedactUI"),
	])

#                      §12345  67890+ Tqwert  yuiopå Casdfghjklöä <zxcvb  nm,.-^
ch("Sym",           """    ¤        ±  …_[]^  !<>=&°  \/{}*?()-:@  #$|~`  +%"';  """) # Inspired by https://neo-layout.org/index_en.html Layer 3
ch("HyperSym",      """                ⫷⫸【】    ‹›«»         ⸨⸩—           „“”‘’  """) # Inspired by http://xahlee.info/comp/unicode_matching_brackets.html
ch("Math",          """         ≡⇔⇒             ↔→         ∘∧∨⊤⊥           ∀∃⊢⊨  """) # Logic-related symbols
ch("Greek",         """                ;ςερτ  υθιοπ   ασδφγηξκλ    ζχψωβ  νμ     """)
ch("ShiftGreek",    """                  ΕΡΤ  ΥΘΙΟΠ   ΑΣΔΦΓΗΞΚΛ    ΖΧΨΩΒ  ΝΜ·    """)
ch("Cyr-",          """                йцуке  нгшщзхъ фывапролджэ  ячсми  тьбю   """)
ch("Cyr-Shift",     """                ЙЦУКЕ  НГШЩЗХЪ ФЫВАПРОЛДЖЭ  ЯЧСМИ  ТЬБЮ   """)
ch("Bats",          """ ♭♮♯♩♪  ♫♬         ✆☎          ✧✦✓➔✗ ◇◆●                  """)
ch("HyperNum",      """                        ₇₈₉          ₄₅₆           ₊₁₂₃₋  """) # Subscript numpad
ch("HyperMath",     """                        ⁷⁸⁹          ⁴⁵⁶           ⁺¹²³⁻  """) # Superscript numpad

load("Sym", [
	("0","space"),
	("Z2","begin_unicode_input"),
	])
load("HyperNum", [
	("D1","₀"),
	("S3","₍"),
	("S2","₎"),
	])
load("HyperMath", [
	("D1","⁰"),
	("S3","⁽"),
	("S2","⁾"),
	])
load("Math", [
	("P", "back"),
	])
load("Cyr-", [
	("Y2", "ъ"),
    ])
load("Cyr-Shift", [
	("Y2", "Ъ"),
    ])

# Composing negation for logic symbols
load("Math", [("U", "compose:¬")])
compose({
	"¬≡": "≢",
	"¬↔": "⊻",
	"¬∧": "⊼",
	"¬∨": "⊽",
	"¬∃": "∄",
	"¬⊢": "⊬",
	"¬⊨": "⊭",
	"¬=": "≠",
	"¬<": "≥",
	"¬>": "≤",
	"¬→": "∧¬",
	})

# Composing superscript and subscript
load("Sym", [
	("5", "compose:^"),
	("3", "compose:^"),
	("2", "compose:_"),
	])
compose({
	"_0":"₀","_1":"₁","_2":"₂","_3":"₃","_4":"₄","_5":"₅","_6":"₆","_7":"₇","_8":"₈","_9":"₉",
	"_A":"ₐ",                           "_E":"ₑ",                  "_H":"ₕ","_I":"ᵢ","_J":"ⱼ",
	"_K":"ₖ","_L":"ₗ","_M":"ₘ","_N":"ₙ","_O":"ₒ","_P":"ₚ",         "_R":"ᵣ","_S":"ₛ","_T":"ₜ",
	"_U":"ᵤ","_V":"ᵥ",         "_X":"ₓ",
	"_+":"₊","_-":"₋","_=":"₌","_(":"₍","_)":"₎",

	"^0":"⁰","^1":"¹","^2":"²","^3":"³","^4":"⁴","^5":"⁵","^6":"⁶","^7":"⁷","^8":"⁸","^9":"⁹",
	"^A":"ᵃ","^B":"ᵇ","^C":"ᶜ","^D":"ᵈ","^E":"ᵉ","^F":"ᶠ","^G":"ᵍ","^H":"ʰ","^I":"ⁱ","^J":"ʲ",
	"^K":"ᵏ","^L":"ˡ","^M":"ᵐ","^N":"ⁿ","^O":"ᵒ","^P":"ᵖ",         "^R":"ʳ","^S":"ˢ","^T":"ᵗ",
	"^U":"ᵘ","^V":"ᵛ","^W":"ʷ","^X":"ˣ","^Y":"ʸ","^Z":"ᶻ",
	"^+":"⁺","^-":"⁻","^=":"⁼","^(":"⁽","^)":"⁾",

	("^", "M4"): "⁻", ("_", "M4"): "₋",
	("^", "02"): "⁺", ("_", "02"): "₊",
	})

# Composing math blackboard bold
load("Math", [("B", "compose:BB")])
compose({
	("BB","N"): "ℕ",
	("BB","Z"): "ℤ",
	("BB","Q"): "ℚ",
	("BB","R"): "ℝ",
	("BB","C"): "ℂ",
	("BB","I"): "ⅈ",
	})

# Composing accents for Greek
load("Greek", [
	("L2", "compose:΄"), # Dead tonos
])
load("ShiftGreek", [
	("L2", "compose:¨"), # Dead diaeresis (used for dialytika)
	("W", "compose:΅"), # Dead dialytika tonos
])
compose({
	"΄Α": "Ά","΄Ε": "Έ","΄Η": "Ή","΄Ι": "Ί","΄Ο": "Ό","΄Υ": "Ύ","΄Ω": "Ώ",
	"΄α": "ά","΄ε": "έ","΄η": "ή","΄ι": "ί","΄ο": "ό","΄υ": "ύ","΄ω": "ώ",
	                              "¨Ι": "Ϊ",          "¨Υ": "Ϋ",
	                              "¨ι": "ϊ",          "¨υ": "ϋ",
	"΄¨": "΅","¨΄": "΅",          "΅ι": "ΐ",          "΅υ": "ΰ",
})

w("Nav",
 ".       .       .      C-S-LTab  C-Tab   .       .                       .       .       .      10*Up      .       .           .                 . " +
 ".       Esc     Alt-F4  C-PgUp   C-PgDn  A-Home  .                       .       .       Home      Up      End     Back        Del               . " +
 ".       A-Left  A-Right S-LTab   Tab     C-Ret                                   .       Left      Down    Right   Ret         Ret,Up,End        . " +
 ".       .       .       .        .       .       .                       .       Ins  10*Left   10*Down 10*Right   S-home,Back S-end,del         . " +
 ".       .       .       .                                                                space,left .      .       .                               " +
 "                                                 .       .       .       .                                                                         " +
 "                                                         .       .                                                                                 " +
 "                                         .       .       .       .       .       space                                                             " )

w("Nav2",
 ".       .       .       .        .       .       .                       .       .       .      10*PgUp    .       .           .                 . " +
 ".       .       .       C-A-lef  C-A-rig .       .                       .       .       C-Home    PgUp    C-End   C-Back      C-Del             . " +
 ".       .       .       S-A-LTab A-Tab   .                                       .       C-Left    PgDn    C-Right S-Ret       .                 . " +
 ".       .       .       .        .       .       .                       .       .    10*C-Left 10*PgDn 10*C-Right .           S-end,S-rig,S-del   " )

load("Nav3",[
	("I", "S-up"),
	("J", "S-left"),
	("K", "S-down"),
	("L", "S-right"),
	("O", "S-end"),
	("U", "S-home"),
	("8", "10*S-up"),
	("M", "10*S-left"),
	("M2","10*S-down"),
	("M3","10*S-right"),
	])

load("Nav4",[
	("I", "S-pgup"),
	("J", "S-C-left"),
	("K", "S-pgdn"),
	("L", "S-C-right"),
	("O", "S-C-end"),
	("U", "S-C-home"),
	("8", "10*S-pgup"),
	("M", "10*S-C-left"),
	("M2","10*S-pgdn"),
	("M3","10*S-C-right"),
	("P2","S-C-right,S-del"),
	("P", "S-C-left,S-del"),
	])

w("WM",
 ".       .       .       .       .       .       .                       .       .       .       .       .       .       .       .       " +
 ".       .       .       .       .       .       .                       .       .       .       s-up    .       .       .       .       " +
 ".       .       .       .       .       .                                       .       s-lef   s-dow   s-rig   .       .       .       " +
 ".       s-1     s-2     s-3     s-4     .       .                       .       .       .       A-F4    .       .       .       .       " +
 ".       .       .       .                                                               .       .       .       .                       " +
 "                                                .       .       .       .                                                               " +
 "                                                        .       .                                                                       " +
 "                                        .       .       .       .       .       space                                                   " )

load("WM",[
	("Q", "A-space,Wait-250,X"),
	("M4","A-space,Wait-250,N"),
	])

for key in planes["from"]:
	if(key): load("X11-WM",[(key, "C-M-section,Wait-100,"+key)])
load("X11-WM",[("Q2", "C-M-section")])

w("Num",
 ".       .       F12     F11     F10     .       .                       .       .e      .a      .b      .c      .d      .f      .       " +
 ".       F12     F9      F8      F7      .       .                       .       /       7       8       9      back    Comma    .       " +
 ".       F11     F6      F5      F4      .                                       *       4       5       6      ret     Period   .       " +
 ".       F10     F3      F2      F1      .       .                       .       +       1       2       3       -       :       .       " +
 ".       .       (       )                                                               0       [       ]       .                       " +
 "                                                .       .       .       .                                                               " +
 "                                                        .       .                                                                       " +
 "                                        .       .       .       .       .       space                                                   " )

load("Shell",[
	("Y", ". \"$dir3\""),
	("H", ". \"$dir2\""),
	("N", ". \"$dir1\""),
	("T", """C-A,C-K,.dir3="`pwd`",Ret"""),
	("G", """C-A,C-K,.dir2="`pwd`",Ret"""),
	("B", """C-A,C-K,.dir1="`pwd`",Ret"""),
	("J", """C-A,C-K,.cd ..,Ret"""),
	("L", """C-A,C-K,.cd ,tab,tab"""),
	("K", """C-A,C-K,.ls -l,Ret"""),
	("M2","""C-A,C-K,.ls -la,Ret"""),
	("I", """C-L"""),
	("O", """C-A,C-K,.cd -,Ret"""),
	("U", """C-A,C-K,.jobs,Ret"""),
	("L2", """C-A,C-K,.ok p,Ret"""),
	("E", """S-pgup"""),
	("D", """S-pgdn"""),
	("F", """C-A,C-K,.history_sync,Ret"""),
	])
load("X11-Shell",[
	("E", "s-XF86ScrollUp"),    # Scroll up
	("D", "s-XF86ScrollDown")]) # Scroll down

load("TeX-Math",[
	("7", ".\\equiv"),
	("8", ".\\Leftrightarrow"),
	("9", ".\\Rightarrow"),
	("U", "compose:.\\neg"),
	("I", ".\\leftrightarrow"),
	("O", ".\\to"),
	("P", "C-back,back"),
	("H", ".\\circ"),
	("J", ".\\land"),
	("K", ".\\lor"),
	("L", ".\\top"),
	("L2",".\\bot"),
	("M", ".\\forall"),
	("M2",".\\exists"),
	("M3",".\\vdash"),
	("M4",".\\models"),
	])
compose({
	(".\\neg",".\\equiv"): ".\\not\\equiv",
	(".\\neg",".\\leftrightarrow"): ".\\veebar",
	(".\\neg",".\\land"): ".\\barwedge",
	(".\\neg",".\\lor"): ".\\bar\\lor",
	(".\\neg",".\\exists"): ".\\nexists",
	(".\\neg",".\\vdash"): ".\\nvdash",
	(".\\neg",".\\models"): ".\\nvDash",
	(".\\neg","="): ".\\neq",
	})

w("TeX-Greek", # lower-case greek letters for TeX
	""".          .          .          .          .          .          .          .          .          .          .          .          .          .          .  """ +
	""".          .         .\\varsigma .\\epsilon .\\rho     .\\tau     .          .          .\\upsilon .\\theta   .\\iota    .\\omicron .\\pi      .          .  """ +
	""".          .\\alpha   .\\sigma   .\\delta   .\\phi     .\\gamma                         .\\eta     .\\xi      .\\kappa   .\\lamda   .          .          .  """ +
	""".          .\\zeta    .\\chi     .\\psi     .\\omega   .\\beta    .          .          .\\nu      .\\mu      .          .          .          .          .  """ )
w("TeX-ShiftGreek", # upper-case greek letters for Tex
	""".          .          .          .          .          .          .          .          .          .          .          .          .          .          .  """ +
	""".          .          .          .\\Epsilon .\\Rho     .\\Tau     .          .          .\\Upsilon .\\Theta   .\\Iota    .\\Omicron .\\Pi      .          .  """ +
	""".          .\\Alpha   .\\Sigma   .\\Delta   .\\Phi     .\\Gamma                         .\\Eta     .\\Xi      .\\Kappa   .\\Lamda   .          .          .  """ +
	""".          .\\Zeta    .\\Chi     .\\Psi     .\\Omega   .\\Beta    .          .          .\\Nu      .\\Mu      .          .          .          .          .  """ )

w("Mirror",
 ".       .       .       Back    Ret     .       .       .       .       .       Ret     Back    .       .       .       " +
 "P2      P       O       I       U       Y       .       .       T       R       E       W       Q       Q2      .       " +
 "L3      L2      L       K       J       H                       G       F       D       S       A       .       .       " +
 ".       M4      M3      M2      M       N       .       .       B       V       C       X       Z       Z2      .       " )

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
 ".       b-das=N b-das=2 b-das=3 b-das=4 .       .                       .       space   b-___R  b-L__R  b-L___  .       .       .       " +
 ".       b-lef=d b-dow=d b-up=d  b-rig=d b-arc=Y .                       .       b-_D__  b-_D_R  b-LD_R  b-LD__  back    del     .       " +
 ".       b-lef=l b-dow=l b-up=l  b-rig=l b-arc=N                                 b-_DU_  b-_DUR  b-LDUR  b-LDU_  ret     ret,up,end .    " +
 ".       b-lef=h b-dow=h b-up=h  b-rig=h .       .                       .       b-__U_  b-__UR  b-L_UR  b-L_U_  .       .       .       " +
 ".       .       .       .                                                                       .       .       .       .               " +
 "                                                .       .       .       .                                                               " +
 "                                                        .       .                                                                       " +
 "                                        .       .       .       .       .       space                                                   " )


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
	("Y", "XF86Red"),         # Toggle light/dark color theme
	("U", "XF86Yellow"),      # Reset zoom
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
	"S3": 20,
	"L": 30,
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
	"composition",
	]
