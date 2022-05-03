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
composition={}
def compose(composedict):
	global composition
	composition={**composition,
		**{tuple(key):composedict[key]
		   for key in composedict}}

w("from",
"""12      1       2       3       4       5       52                      62      6       7       8       9       0       02      """ +
"""Q2      Q       W       E       R       T       T2                      Y2      Y       U       I       O       P       P2      """ +
"""A2      A       S       D       F       G                                       H       J       K       L       L2      L3      """ +
"""Z2      Z       X       C       V       B       B2                      N2      N       M       M2      M3      M4      M5      """ +
"""                S3      S2                                                              D1      D2      D3                      """ +
"""                                                SC1     SC2     DC2     DC1                                                     """ +
"""                                                        SC3     DC3                                                             """ +
"""                                        Back    Del     SC4     DC4     Ret     space                                           """ )

w("mods",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       .       .       mods    .       .       .                       .       .       .       .       .       .       .       """ +
"""Super   Macro   WM      Nav2    Nav3    Nav4    .                       .       .       Modlock Nav2    WM      Univ    Super   """ +
"""Hyper   Ctrl    Alt     Nav     Sym     Greek                                   Greek   Sym     Nav     Alt     Ctrl    Hyper   """ +
"""Shell   Shift   Meta    Num     Logic   Bats    .                       .       Bats    Logic   Num     Meta    Shift   Shell   """ +
"""                .       .                                                               .       .       .                       """ +
"""                                                .       .       .       .                                                       """ +
"""                                                        .       .                                                               """ +
"""                                        .       .       .       .       Nav2WM  WM                                              """ )

load("modes",[
	("X", "+X11,-Win"),
	("W", "+Win,-X11"),
	("C", "^Cyr,-Box"),
	("B", "^Box,-Cyr"),
	("M2", "^HEX"),
	("R", "+RedactUI"),
	("4", "-RedactUI"),
	])

##### Default and shift layers #####
w("",
"""§       1       2       3       4       5       .                       .       6       7       8       9       0       +       """ +
""".       q       w       e       r       t       .                       .       y       u       i       o       p       å       """ +
""".       a       s       d       f       g                                       h       j       k       l       ö       ä       """ +
"""<       z       x       c       v       b       .                       .       n       m       ,       Period  -       .       """ )
w("Shift",
""".       !       "       #       ¤       %       .                       .       &       /       (       )       =       ?       """ +
""".       Q       W       E       R       T       .                       .       Y       U       I       O       P       Å       """ +
""".       A       S       D       F       G                                       H       J       K       L       Ö       Ä       """ +
""">       Z       X       C       V       B       .                       .       N       M       ,       Period  -       .       """ )
# Latin character composition
load("", [("A2", "compose: ")])
import unicodedata
def unicodeget(name):
	try: return unicodedata.lookup(name)
	except KeyError: return None
for (diacritic, suffix) in [
		("acute",                   "s"),
		#("acute and dot above",     "y"),
		("caron",                   "v"),
		#("caron and dot above",     "u"),
		("cedilla",                 "c"),
		("circumflex",              "t"),
		#("comma below",             ","),
		#("curl",                    ""),
		#("descender",               "l"),
		("diaeresis",               "e"),
		("dot above",               "g"),
		("dot below and dot above", ":"),
		("dot below",               "Period"),
		("grave",                   "a"),
		#("hook",                    "h"),
		#("line below",              "w"),
		#("low line",                "W"),
		#("middle tilde",            ""),
		#("oblique stroke",          ""),
		#("palatal hook",            "j"),
		#("retroflex hook",          ""),
		#("stroke",                  ""),
		#("swash tail",              "t"),
]:
	combining=unicodeget(f"combining {diacritic}")
	if combining:
		compose({(" ", "Period", suffix): combining})
	for base in "abcdefghijklmnopqrstuvwxyz":
		for (capital, letter) in [("capital", base.upper()), ("small", base)]:
			target=unicodeget(f"latin {capital} letter {letter} with {diacritic}")
			if target:
				compose({(" ", letter, suffix): f".{target}"})
			elif combining:
				compose({(" ", letter, suffix): f".{letter}{combining}"})
compose({
# Old english
	" Th": "Þ", " th": "þ", # thorn
	" Dh": "Ð", " dh": "ð", # eth
	" AE": "Æ", " aE": "æ", # ash ;Also in Modern nordic
	" Wh": "Ƿ", " wh": "ƿ", # wynn
	" Gh": "Ȝ", " gh": "ȝ", # yogh
	" OE": "Œ", " oE": "œ", # ethel
	" Ng": "Ŋ", " ng": "ŋ", # eng
	" sf": "ſ",             # long s
	#                         insular g
	#                         that
	#                         tironian ond
# Modern nordic
	" Ao": "Å", " ao": "å",
	" AE": "Æ", " aE": "æ",
	" O-": "Ø", " o-": "ø",
})
# Prevent fallthrough for some keys
for key in [
            "52", "62",
            "T2", "Y2",
            "B2", "N2",
            "S3", "S2", "D1", "D2", "D3",
            "SC1", "SC2", "DC2", "DC1",
            "SC3", "DC3",
            "SC4", "DC4",
]:
	load("", [(key, ".")])

##### Symbolic layer #####
# Inspired by https://neo-layout.org/Layouts/neoqwertz/ (see layer 3, or
# "Ebene 3")
w("Sym",
#   §       1       2       3       4       5                                       6       7       8       9       0       +
r""".       .       .       .       ¤       .       .                       .       .       .       .       .       space   ±       """ +
r""".       …       _       [       ]       ^       .                       .       !       <       >       =       &       °       """ +
r""".       \       /       {       }       *                                       ?       (       )       -       :       @       """ +
r"""unicode #       $       |       ~       `       .                       .       +       %       "       '       ;       .       """ )
# Composing superscript and subscript
load("Sym", [
	("5", "compose:^"),
	("3", "compose:^"),
	("2", "compose:_"),
	])
for (char, subscript, supscript) in zip(
	"0123456789abcdefghijklmnopqrstuvwxyz+-=()",
	"₀₁₂₃₄₅₆₇₈₉ₐ   ₑ  ₕᵢⱼₖₗₘₙₒₚ ᵣₛₜᵤᵥ ₓ  ₊₋₌₍₎",
	"⁰¹²³⁴⁵⁶⁷⁸⁹ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖ ʳˢᵗᵘᵛʷˣʸᶻ⁺⁻⁼⁽⁾"):
	if(subscript!=" "): compose({f"_{char}": subscript})
	if(supscript!=" "): compose({f"^{char}": supscript})

##### Numpad layer #####
w("Num",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       .       F12     F11     F10     .       .                       .       .e      .a      .b      .c      .d      .f      """ +
""".       F12     F9      F8      F7      .       .                       .       /       7       8       9      back    Comma    """ +
""".       F11     F6      F5      F4      .                                       *       4       5       6      ret     Period   """ +
""".       F10     F3      F2      F1      .       .                       .       +       1       2       3       -       :       """ +
"""                (       )                                                               0       [       ]                       """ +
"""                                                .       .       .       .                                                       """ +
"""                                                        .       .                                                               """ +
"""                                        .       .       .       .       .       space                                           """ )
# Capital hexadecimals
w("HEX-Num",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       .       .       .       .       .       .                       .       .E      .A      .B      .C      .D      .F      """ )
# Subscript and superscript numpads
w("HyperNum",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       .       .       .       .       .       .                       .       .       .       .       .       .       .       """ +
""".       .       .       .       .       .       .                       .       .       ₇       ₈       ₉       .       .       """ +
""".       .       .       .       .       .                                       .       ₄       ₅       ₆       .       .       """ +
""".       .       .       .       .       .       .                       .       ₊       ₁       ₂       ₃       ₋       .       """ +
"""                ₍       ₎                                                               ₀       .       .                       """ )
w("HyperLogic",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       .       .       .       .       .       .                       .       .       .       .       .       .       .       """ +
""".       .       .       .       .       .       .                       .       .       ⁷       ⁸       ⁹       .       .       """ +
""".       .       .       .       .       .                                       .       ⁴       ⁵       ⁶       .       .       """ +
""".       .       .       .       .       .       .                       .       ⁺       ¹       ²       ³       ⁻       .       """ +
"""                ⁽       ⁾                                                               ⁰       .       .                       """ )

##### Brackets layer #####
# Inspired by http://xahlee.info/comp/unicode_matching_brackets.html
w("HyperSym",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       .       .       .       .       .       .                       .       .       .       .       .       .       .       """ +
""".       ⫷      ⫸      【      】      .       .                       .       .       ‹       ›       «       »       .       """ +
""".       .       .       .       .       .                                       .       ⸨       ⸩       —       .       .       """ +
""".       .       .       .       .       .       .                       .       „       “       ”       ‘       ’       .       """ )

##### Logic-related symbols #####
w("Logic",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       .       .       .       .       .       .                       .       .       ≡       ⇔       ⇒       .       .       """ +
""".       .       .       .       .       .       .                       .       .       .       ↔       →       back    .       """ +
""".       .       .       .       .       .                                       ∘       ∧       ∨       ⊤       ⊥       .       """ +
""".       .       .       .       .       .       .                       .       .       ∀       ∃       ⊢       ⊨       .       """ )
# Composing negation for logic symbols
load("Logic", [("U", "compose:¬")])
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
# Composing math blackboard bold
load("Logic", [("B", "compose:𝔸")])
compose({
	"𝔸n": "ℕ",
	"𝔸z": "ℤ",
	"𝔸q": "ℚ",
	"𝔸r": "ℝ",
	"𝔸c": "ℂ",
	"𝔸i": "ⅈ",
	})

##### Greek layers #####
w("Greek",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       .       .       .       .       .       .                       .       .       .       .       .       .       .       """ +
""".       ;       ς       ε       ρ       τ       .                       .       υ       θ       ι       ο       π       .       """ +
""".       α       σ       δ       φ       γ                                       η       ξ       κ       λ       .       .       """ +
""".       ζ       χ       ψ       ω       β       .                       .       ν       μ       .       .       .       .       """ )
w("ShiftGreek",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       .       .       .       .       .       .                       .       .       .       .       .       .       .       """ +
""".       .       .       Ε       Ρ       Τ       .                       .       Υ       Θ       Ι       Ο       Π       .       """ +
""".       Α       Σ       Δ       Φ       Γ                                       Η       Ξ       Κ       Λ       .       .       """ +
""".       Ζ       Χ       Ψ       Ω       Β       .                       .       Ν       Μ       ·       .       .       .       """ )
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

##### Cyrillic layers #####
w("Cyr-",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       .       .       .       .       .       .                       .       .       .       .       .       .       .       """ +
""".       й       ц       у       к       е       .                       ъ       н       г       ш       щ       з       х       """ +
""".       ф       ы       в       а       п                                       р       о       л       д       ж       э       """ +
""".       я       ч       с       м       и       .                       .       т       ь       б       ю       .       .       """ )
w("Cyr-Shift",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       .       .       .       .       .       .                       .       .       .       .       .       .       .       """ +
""".       Й       Ц       У       К       Е       .                       Ъ       Н       Г       Ш       Щ       З       Х       """ +
""".       Ф       Ы       В       А       П                                       Р       О       Л       Д       Ж       Э       """ +
""".       Я       Ч       С       М       И       .                       .       Т       Ь       Б       Ю       .       .       """ )

##### Dingbats layer #####
w("Bats",
#  §       1       2       3       4       5                                       6       7       8       9       0       +
""".       ♭       ♮       ♯       ♩       ♪       .                       .       ♫       ♬       .       .       .       .       """ +
""".       .       .       .       ✆       ☎       .                       .       .       .       .       .       .       .       """ +
""".       ✧       ✦       ✓       ➔       ✗                                       .       ◇       ◆       ●       .       .       """ +
""".       .       .       .       .       .       .                       .       .       .       .       .       .       .       """ )

##### Navigation layers #####
w("Nav",
# § 1      2       3        4       5              6       7         8          9          0             +
 ". .      .       C-S-LTab C-Tab   .      .     . .       .      10*Up         .          .             .                 " +
 ". Esc    Alt-F4  C-PgUp   C-PgDn  A-Home .     . .       Home      Up         End        Back          Del               " +
 ". A-Left A-Right S-LTab   Tab     C-Ret          .       Left      Down       Right      Ret           Ret,Up,End        " +
 ". .      .       .        .       .      .     . Ins  10*Left   10*Down    10*Right      S-home,Back   S-end,del         " +
 "         .       .                                       space,left .         .                                          " +
 "                                         . . . .                                                                         " +
 "                                           . .                                                                           " +
 "                                  .      . . . . space                                                                   " )
w("Nav2",
# § 1      2       3        4       5              6       7         8          9          0             +
 ". .      .       .        .       .      .     . .       .      10*PgUp       .          .             .                 " +
 ". .      .       C-A-lef  C-A-rig .      .     . .       C-Home    PgUp       C-End      C-Back        C-Del             " +
 ". .      .       S-A-LTab A-Tab   .              .       C-Left    PgDn       C-Right    S-Ret         .                 " +
 ". .      .       .        .       .      .     . .    10*C-Left 10*PgDn    10*C-Right    .             S-end,S-rig,S-del " )
w("Nav3",
# § 1      2       3        4       5              6       7         8          9          0             +
 ". .      .       .        .       .      .     . .       .      10*S-up       .          .             .                 " +
 ". .      .       .        .       .      .     . .       S-home    S-up       S-end      .             .                 " +
 ". .      .       .        .       .              .       S-left    S-down     S-right    .             .                 " +
 ". .      .       .        .       .      .     . .    10*S-left 10*S-down  10*S-right    .             .                 " )
w("Nav4",
# § 1      2       3        4       5              6       7         8          9          0             +
 ". .      .       .        .       .      .     . .       .      10*S-pgup     .          .             .                 " +
 ". .      .       .        .       .      .     . .       S-C-home  S-pgup     S-C-end    S-C-lef,S-del S-C-rig,S-del     " +
 ". .      .       .        .       .              .       S-C-left  S-pgdn     S-C-rig    .             .                 " +
 ". .      .       .        .       .      .     . .    10*S-C-lef 10*S-pgdn 10*S-C-rig    .             .                 " )

##### Window management layers #####
w("WM",
# § 1      2       3        4       5              6       7         8          9          0             +
 ". .      .       .        .       .      .     . .       .         .          .          .             .                 " +
 ". .      .       .        .       .      .     . .       .         s-up       .          .             .                 " +
 ". .      .       .        .       .              .       s-lef     s-dow      s-rig      .             .                 " +
 ". s-1    s-2     s-3      s-4     .      .     . .       .         A-F4       .          .             .                 " +
 "         .       .                                       .         .          .                                          " +
 "                                         . . . .                                                                         " +
 "                                           . .                                                                           " +
 "                                  .      . . . . space                                                                   " )
load("WM",[
	("Q", "A-space,Wait-250,X"),
	("M4","A-space,Wait-250,N"),
	])
for key in planes["from"]:
	if(key):
		load("X11-WM",[(key, "C-M-section,Wait-100,"+key)])
		load("X11-Nav2WM",[(key, "C-M-section,Wait-100,C-"+key)])
load("X11-WM",[("Q2", "C-M-section")])

##### Shell layer #####
load("Shell",[
	("Y", ". \"$dir3\""),
	("H", ". \"$dir2\""),
	("N", ". \"$dir1\""),
	("T", """Home,C-K,.dir3="`pwd`",Ret"""),
	("G", """Home,C-K,.dir2="`pwd`",Ret"""),
	("B", """Home,C-K,.dir1="`pwd`",Ret"""),
	("J", """Home,C-K,.cd ..,Ret"""),
	("L", """Home,C-K,.cd ,tab,tab"""),
	("K", """Home,C-K,.ls -l,Ret"""),
	("M2","""Home,C-K,.ls -la,Ret"""),
	("I", """C-L"""),
	("O", """Home,C-K,.cd -,Ret"""),
	("U", """Home,C-K,.jobs,Ret"""),
	("L2", """Home,C-K,.ok p,Ret"""),
	("E", """S-pgup"""),
	("D", """S-pgdn"""),
	("F", """Home,C-K,.history_sync,Ret"""),
	])
load("X11-Shell",[
	("E", "s-XF86ScrollUp"),    # Scroll up
	("D", "s-XF86ScrollDown")]) # Scroll down

##### Box drawing layer #####
w("Box-",
# §       1       2       3       4       5                                       6       7       8       9       0       +
 ".       b-das=N b-das=2 b-das=3 b-das=4 .       .                       .       space   b-___R  b-L__R  b-L___  .       .          " +
 ".       b-lef=d b-dow=d b-up=d  b-rig=d b-arc=Y .                       .       b-_D__  b-_D_R  b-LD_R  b-LD__  back    del        " +
 ".       b-lef=l b-dow=l b-up=l  b-rig=l b-arc=N                                 b-_DU_  b-_DUR  b-LDUR  b-LDU_  ret     ret,up,end " +
 ".       b-lef=h b-dow=h b-up=h  b-rig=h .       .                       .       b-__U_  b-__UR  b-L_UR  b-L_U_  .       .          " +
 "                .       .                                                                       .       .       .                  " +
 "                                                .       .       .       .                                                          " +
 "                                                        .       .                                                                  " +
 "                                        .       .       .       .       .       space                                              " )

##### Universals layer #####
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

##### Non-layer configuration #####

nativemods=set(["Super", "Hyper", "Meta", "Alt", "Ctrl", "Shift"])

# List and priority of native modifier combinations allowed as prefixes to plane
# names together with what modifiers to leave in effect. The empty list
# represents an exact match between non-native modifiers and plane name.
planeprefixes=[
	({"Shift"}, {"Shift"}),
	({"Hyper"}, set()),
	(set(), set()),
	]

# List of the modifier combinations that will allow a compose sequence to
# continue.
composenonbreakmodsets=[
	set(),
	{"Shift"},
	]

# List and priority of mode combinations together with allowed effective mods.
# The empty set represents ignoring all modes and allowing no effective mods,
# respectively.
modespriority=[
	({"Win"},set()),
	({"X11"},{"Ctrl"}),
	({"Box"},set()),
	({"Cyr"},set()),
	({"HEX"},set()),
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

__all__=[
	"nativemods",
	"planeprefixes",
	"modespriority",
	"modnotation",
	"planelookup",
	"max_numarg_digits",
	"composition",
	]
