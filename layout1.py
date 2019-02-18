from libkeyboa import *
from layout1_commonname import *

planes={}

def load(plane, iter):
	if(not plane in planes):
		planes[plane]=[]
	pl=planes[plane]
	for i, elem in enumerate(iter):
		if(elem):
			while(len(pl)<=i):
				pl.append(None)
			pl[i]=elem
def w(plane, string):
	def f():
		for word in string.split(" "):
			if(word==""):
				pass
			elif(word=="."):
				yield None
			else:
				yield word
	load(plane, f())
def ch(plane, string):
	def f():
		for char in string:
			if(char==" "):
				char=None
			yield char
	load(plane, f())

#                      §1234567890+TqwertyuiopåCasdfghjklöä<zxcvbnm,.-^
ch("Sym",           """ ⁿ²³   0,. ± …_[]^!<>=&  \/{}*?()-:@ #$|~`+%"'; """) #°
ch("Greek",         """              ςερτυθιοπ  ασδφγηξκλ   ζχψωβνμ    """)
ch("ShiftGreek",    """               ΕΡΤΥΘΙΟΠ  ΑΣΔΦΓΗΞΚΛ   ΖΧΨΩΒΝΜ    """)
ch("Cyrillic",      """             йцукенгшщзх фывапролджэ ячсмитьбю- """)
ch("ShiftCyrillic", """                                                """)
ch("Math",          """             ⋀⋁∈ ⇒ ≈∞∅∝  ∀∫∂f⊂⊃ ⇔   ≤ ∃  ⇐ℕℤℚℝℂ """)
ch("ShiftMath",     """          ≠  ⋂⋃∉ ∴ ≉      ∮  ⊏⊐      ≥∄  ∵∇     """)

w("from",
 "12 1 2 3 4 5 6 7 8  9  0  02 " +
 "Q2 Q W E R T Y U I  O  P  P2 " +
 "A2 A S D F G H J K  L  L2 L3 " +
 "Z2 Z X C V B N M M2 M3 M4 M5 " )

w("Nav",
 ". .   . . . . . .    10*Up   .     .    .   " +
 ". Esc . . . . . Home Up      End   Back Del " +
 ". .   . . . . . Left Down    Right Ret  .   " +
 ". .   . . . . . .    10*Down .     .    .   " )

w("Nav2",
 ". . . . . . . .      10*PgUp .       .    .   " +
 ". . . . . . . C-Home PgUp    C-End   Back Del " +
 ". . . . . . . C-Left PgDn    C-Right Ret  .   " +
 ". . . . . . . .      10*PgDn .       .    .   " )

w("Num",
 ". .   F12 F11 F10 . . 0  M2 M3 space . " +
 ". F12 F9  F8  F7  . ( 7  8  9  back  / " +
 ". F11 F6  F5  F4  . ) 4  5  6  ret   * " +
 ". F10 F3  F2  F1  . + 1  2  3  -     : " )

modplanes = [
	("A",  "L2", "Ctrl"),
	("S5",  "T4", "Ctrl"),
	("S",  "L",  "Alt"),
	("S2",  None,  "Alt"),
	(None, "T2", "AltGr"),
	("Z",  "M4", "Shift"),
	("Z3",  "M5", "Shift"),
	("D",  "K",  "Nav"),
	("E",  "I",  "Nav2"),
	("F",  "J",  "Sym"),
	("G",  "H",  "Greek"),
	("X",  "M3", "Meta"),
	("C",  "M2", "Num"),
	("V",  "M",  "Math"),
	("B",  "N",  "Cyrillic"),
	("W",  "O",  "WM")]
modmap={}
for (left, right, mod) in modplanes:
	if(left):
		modmap[left]=mod
	if(right):
		modmap[right]=mod

planeprefixes=[
	["Ctrl","Alt","Shift"],
	["Alt","Shift"],
	["Ctrl","Shift"],
	["Ctrl","Alt"],
	["Shift"],
	["Alt"],
	["Ctrl"],
	[]]

modnotation={
	"C": "Ctrl",
	"A": "Alt",
	"S": "Shift"}

def chordmachine(gen):
	for obj in gen:
		type=obj["type"]
		if(type=="chord"):
			inchord=obj["chord"]
			inmods=inchord[:-1]
			inkey=inchord[-1]
			planemods=set()
			nativemods=set()
			for mod in inmods:
				if(mod in modmap):
					mod=modmap[mod]
				if(mod in ["Ctrl", "Alt", "Shift"]):
					nativemods.add(mod)
				else:
					planemods.add(mod)
			out=None
			outmods=set()
			planename="".join(sorted(planemods))
			i=None
			if(inkey in planes["from"]):
				i=planes["from"].index(inkey)
			for pre in planeprefixes:
				pl="".join(pre)+planename
				if(i
				   and pl in planes
				   and set(pre)<=nativemods
				   and i<len(planes[pl])
				   and planes[pl][i]):
					outmods=nativemods-set(pre)
					out=planes[pl][i]
					break
			if(not out):
				outmods=nativemods.union(planemods)
				out=inkey
			#interprete chord string expression
			if(not isinstance(out,str) or len(out)==0):
				raise Exception("Chord expression must be non-empty string")
			if(len(out)==1):
				yield {"type":"chord","chord":
					[*sorted(outmods), out]}
			else:
				for item in out.split(","):
					itemch=item.split("-")
					itemmods=itemch[:-1]
					itemkey=itemch[-1]
					sendmods=set()
					for mod in itemmods:
						if mod in modnotation:
							sendmods.add(modnotation[mod])
						else:
							sendmods.add(mod)
					if("*" in itemkey):
						mulindex=itemkey.index("*")
						repeat=int(itemkey[:mulindex])
						itemkey=itemkey[mulindex+1:]
						yield {"type":"chord","chord":
							[*sorted(sendmods.union(outmods)), itemkey],
							"repeat":repeat}
					else:
						yield {"type":"chord","chord":
							[*sorted(sendmods.union(outmods)), itemkey]}
		else:
			yield obj

list_of_transformations = [
	input,                           # libkeyboa
	releaseall_at_init,              # libkeyboa
	enrich_input,                    # libkeyboa
	add_common_name,                 # common_name
	allow_repeat("physkey"),         # libkeyboa
	events_to_chords("common_name"), # libkeyboa
	chordmachine,                    # Customization from this file
	chords_to_events("common_name"), # libkeyboa
	resolve_common_name,             # common_name
	sendkey_cleanup,                 # libkeyboa
	output]                          # libkeyboa

keyboa_run(list_of_transformations)
