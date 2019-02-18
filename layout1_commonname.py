from libkeyboa import vkeyinfo

_commonname_mapping={
	"OEM_5":        "12",
	"TAB":          "Q2",
	"CAPITAL":      "A2",
	"OEM_102":      "Z2",
	"LSHIFT":       "Z3",

	"OEM_PLUS":     "02",
	"OEM_4":        "03",
	"OEM_6":        "P2",
	"OEM_1":        "P3",
	"OEM_3":        "L2",
	"OEM_7":        "L3",
	"OEM_2":        "L4",
	"OEM_COMMA":    "M2",
	"OEM_PERIOD":   "M3",
	"OEM_MINUS":    "M4",
	"RSHIFT":       "M5",

	"RMENU":        "T2",
	"APPS":         "T3",
	"RCONTROL":     "T4",

	"LMENU":        "S2",
	"LWIN":         "S3",
	"LCONTROL":     "S5"
	}

_aliases={
	"Ctrl":         "VK_LCONTROL",
	"Alt":          "VK_LMENU",
	"LAlt":         "VK_LMENU",
	"RAlt":         "VK_RMENU",
	"AltGr":        "VK_RMENU",
	"Shift":        "VK_SHIFT",
	"LShift":       "VK_LSHIFT",
	"RShift":       "VK_RSHIFT",
	"esc":          "ESCAPE",
	"del":          "DELETE",
	"ret":          "RETURN",
	"enter":        "RETURN",
	"PgUp":         "PRIOR",
	"PgDown":       "NEXT",
	"PgDn":         "NEXT",
	"ins":          "INSERT",
	"sp":           "SPACE",
	"SpaceBar":     "SPACE",
	"Caps":         "CAPITAL",
	"CapsLock":     "CAPITAL"
}

vkey_cn_map = {}
cn_vkey_map = {}

def _alias(vsym, vkey):
	cn_vkey_map[vsym]=vkey
for vkey in range(256):
	#vsym is the primary cn that goes into vkey_cn_map.
	#cn_vkey_map in contrast holds aliases as well
	vsym=vkey
	_alias(vsym, vkey)
	i=vkeyinfo(vkey)
	if(0x30 <= vkey and vkey <= 0x39
	   or 0x41 <= vkey and vkey <= 0x5a):
		vsym=chr(vkey)
		_alias(vsym, vkey)
	if("win_virtualkey_symbol" in i and i["win_virtualkey_symbol"]):
		vsym=i["win_virtualkey_symbol"]
		_alias(vsym, vkey)
	if(isinstance(vsym,str) and vsym[:3]=="VK_"):
		vsym=vsym[3:]
		_alias(vsym, vkey)
	if(vsym in _commonname_mapping):
		vsym=_commonname_mapping[vsym]
		_alias(vsym, vkey)
	vkey_cn_map[vkey]=vsym
for vsymalias, target in _aliases.items():
	_alias(vsymalias, cn_vkey_map[target])
for vsymalias, vkey in {**cn_vkey_map}.items():
	if(isinstance(vsymalias,str)):
		_alias(vsymalias.lower(), vkey)
		_alias(vsymalias.upper(), vkey)
		_alias(vsymalias.title(), vkey)

def add_common_name(gen):
	for obj in gen:
		ret=obj
		if(obj["type"] in ["keydown", "keyup", "keypress"]
		   and "win_virtualkey" in obj):
			vkey=obj["win_virtualkey"]
			cn=vkey_cn_map[vkey]
			if(cn):
				ret={**ret, "common_name": cn}
		yield ret

def resolve_common_name(gen):
	for obj in gen:
		ret=obj
		if(obj["type"] in ["keydown", "keyup", "keypress"]
		   and "common_name" in obj):
			cn=obj["common_name"]
			if(cn in cn_vkey_map):
				vkey=cn_vkey_map[cn]
				ret={**ret, **vkeyinfo(vkey)}
			elif(len(cn)==1):
				ret={**ret, "unicode_codepoint":ord(cn)}
		yield ret

#Test the mappings
for vkey in range(256):
	if(cn_vkey_map[vkey_cn_map[vkey]]!=vkey):
		raise Exception("vkey " + str(vkey) + " failed to map back.")
