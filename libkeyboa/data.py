# Requires python3

# Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
# This file is part of keyboa version <VERSION>
# License: See LICENSE

import os, csv

def absrelfile(file, relfile):
	dir=os.path.dirname(relfile)
	absdir=os.path.abspath(dir)
	absfile=os.path.join(absdir, file)
	return absfile

def fromcsv(filename, relativetofile=__file__):
	file=absrelfile(filename, relativetofile)
	return csv.reader(
		filter(lambda x:not x.startswith("#"), # Remove comments
			   open(file)),
		lineterminator='\n',
		quotechar='"',
		quoting=0,
		delimiter=',',
		skipinitialspace=True,
		doublequote=True)

# Use the table of windows virtual keys in win_vkeys.csv to build a dictionary.
# It can be accessed through the vkeyinfo function using either a numeric or
# symbolic virtual key. It returns a dictionary with the fields win_virtualkey,
# win_virtualkey_symbol, and win_virtualkey_description.

_vkeysdict={}
for (win_virtualkey, win_virtualkey_symbol, win_virtualkey_description) in [
		(int(x,16), None if y=="" else y, z)
		for [x, y, z]
		in fromcsv("win_vkeys.csv")]:
	item={
		"win_virtualkey": win_virtualkey,
		"win_virtualkey_symbol": win_virtualkey_symbol,
		"win_virtualkey_description": win_virtualkey_description}
	if(win_virtualkey):
		_vkeysdict[win_virtualkey]=item
	if(win_virtualkey_symbol):
		_vkeysdict[win_virtualkey_symbol]=item
for vk in list(range(0x30,0x3a))+list(range(0x41,0x5b)):
	_vkeysdict[chr(vk)]=_vkeysdict[vk]

def vkeyinfo(vkey):
	try:
		return _vkeysdict[vkey]
	except KeyError:
		return {}

# Use the table of linux/vnc keysyms in keysyms.csv to build a dictionary.
# It can be accessed through the keysyminfo function using either a numeric or
# symbolic keysym. It returns a dictionary with the fields x11_keysym,
# x11_keysym_symbol, x11_keysym_description and unicode_codepoint
_keysymsdict={}
def _keysymobj_compareby(obj):
	return [
		obj["x11_keysym_description"]=="deprecated",
		obj["x11_keysym_description"].startswith("Alias for "),
		obj["x11_keysym_description"].startswith("Same as "),
		len(obj["x11_keysym_symbol"])]
for (keysym, keysym_symbol, keysym_description, unicode_codepoint) in [
		(int(n, 16), s, d, None if u=="" else int(u, 16))
		for [n, s, d, u]
		in fromcsv("keysyms.csv")]:
	item={"x11_keysym": keysym,
		  "x11_keysym_symbol": keysym_symbol,
		  "x11_keysym_description": keysym_description,
		  "unicode_codepoint": unicode_codepoint}
	save=_keysymsdict[keysym] if keysym in _keysymsdict else item
	if(_keysymobj_compareby(item) <
	   _keysymobj_compareby(save)):
		save["x11_keysym_symbol"]=item["x11_keysym_symbol"]
		save["x11_keysym_description"]=item["x11_keysym_description"]
		save["unicode_codepoint"]=item["unicode_codepoint"]
	_keysymsdict[keysym]=save
	_keysymsdict[keysym_symbol]=save

def keysyminfo(x):
	if(isinstance(x,int)):
		try: return _keysymsdict[x]
		except KeyError: pass
	if(isinstance(x,str)):
		for (prefix, replacement) in [
				("", ""),
				("XKB_KEY_", ""),
				("apXK_", "ap"),
				("SunXK_", "Sun"),
				("hpXK_", "hp"),
				("DXK_", "D"),
				("osfXK_", "osf"),
				("XF86XK_", "XF86")]:
			if(x.startswith(prefix)):
				try: return _keysymsdict[replacement+x[(len(prefix)):]]
				except KeyError: pass
	return {}

# Use the table of common names in commonname.csv to add information to
# - A new dictionary commonnamesdict
# - _keysymsdict
# - _vkeysdict

commonnamesdict={}

def add_commonname_mapping(commonname, keysym_symbol, vkey_symbol):
	item=(commonnamesdict[commonname]
		  if commonname in commonnamesdict
		  else {"commonname": commonname})
	keysym_obj=keysyminfo(keysym_symbol)
	if(keysym_obj):
		keysym_obj["commonname_obj"]=item
		if("keysym_obj" not in item):
			item["keysym_obj"]=keysym_obj
	vkey_obj=vkeyinfo(vkey_symbol)
	if(vkey_obj):
		vkey_obj["commonname_obj"]=item
		if("vkey_obj" not in item):
			item["vkey_obj"]=vkey_obj
	commonnamesdict[commonname]=item

def add_commonname_alias(newname, oldname, newname_is_default=False):
	commonnamesdict[newname]=commonnamesdict[oldname]
	if(newname_is_default):
		commonnamesdict[newname]["commonname"]=newname

for (commonname, keysym_symbol, vkey_symbol) in [
		(x, None if y=="" else y, None if z=="" else z)
		for [x, y, z]
		in fromcsv("commonname.csv")]:
	add_commonname_mapping(commonname, keysym_symbol, vkey_symbol)

def commonnameinfo(cn):
	for key in [cn, cn.lower()]:
		if(key in commonnamesdict):
			return commonnamesdict[key]
	return {}

# Use the table in boxdrawings.csv to populate _boxdict

_boxdict={}
for (code, char, prop, desc) in [
		(int(a,16), b, None if c=="" else c, d)
		for [a, b, c, d]
		in fromcsv("boxdrawings.csv")]:
	d={"code":code, "char":char, "prop": prop, "desc":desc}
	_boxdict[code]=d
	_boxdict[char]=d
	if(prop):
		_boxdict[prop]=d
	_boxdict[desc]=d

def boxdrawings_bestmatch(prop):
	ldur=prop[:4]
	if(len(ldur.split("h"))>len(ldur.split("d"))):
		ldur_=ldur.replace("d", "h")
	else:
		ldur_=ldur.replace("h", "d")
	d=prop[4]
	a=prop[5]
	candidates=[
		ldur + d + a ,
		ldur + d +"N",
		ldur +"N"+ a ,
		ldur +"N"+"N",
		ldur_+ d + a ,
		ldur_+ d +"N",
		ldur_+"N"+ a ,
		ldur_+"N"+"N"]
	for candidate in candidates:
		if(candidate in _boxdict):
			return _boxdict[candidate]
	return None

__all__ = [
	"vkeyinfo",
	"keysyminfo",
	"add_commonname_mapping",
	"add_commonname_alias",
	"commonnameinfo",
	"boxdrawings_bestmatch"]
