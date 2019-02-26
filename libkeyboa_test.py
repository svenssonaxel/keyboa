#!/usr/bin/env python3

from libkeyboa import *
import functools

def stack_tr(stack):
	def ret(input):
		yield from functools.reduce((lambda x, y: y(x)), stack, input)
	return ret

def testtransformation(stack, title, input, output):
	state=[]
	def inputgen(state):
		for obj in input:
			state.append([])
			yield obj
	tr=stack_tr(stack)
	asdf=tr(inputgen(state))
	for item in asdf:
		state[-1].append(item)
	if(state==output):
		print("Test OK: " + str(title))
	else:
		print("Test FAILED: " + str(title) + "\n")
		print("Expected output:\n" + str(output) + "\n")
		print("Actual output:\n" + str(state) + "\n")
		raise Exception("Test failed")

def unchanged(input):
	ret=[]
	for item in input:
		ret.append([item])
	return ret

def dummy_transformation(gen):
	for obj in gen:
		for _ in range(obj["repeat"]):
			yield obj["data"]

testtransformation(
	[dummy_transformation],
	"testtransformation",
	[{"repeat":1, "data":"a"},
	 {"repeat":2, "data":"b"},
	 {"repeat":0, "data":"c"},
	 {"repeat":2, "data":"d"},
	 {"repeat":0, "data":"e"}],
	[["a"],["b","b"],[],["d","d"],[]])

testtransformation([releaseall_at_init], "releaseall_at_init",
	[{"type":"init","platform":"windows","vkeysdown":[13]},
	 {"type":"keydown","win_virtualkey": 65},
	 {"type":"keyup"  ,"win_virtualkey": 65}],
	[[{"type":"init","platform":"windows","vkeysdown":[13]},{"type":"output","data":{"type":"keyup","win_virtualkey":13}}],
	 [{"type":"keydown","win_virtualkey": 65}],
	 [{"type":"keyup"  ,"win_virtualkey": 65}]])

initmsg={"type":"init","platform":"windows","keyboard_type":111,
	"keyboard_subtype":222,"function_keys":333,"OEMCP":444,"oem_mapping":[1,2,3],
	"key_names":[
	{"scancode":1001,"extended":False,"keyname":"first"},
	{"scancode":2002,"extended":False,"keyname":"Second"},
	{"scancode":3003,"extended":True,"keyname":"THIRD"}]}
keyboard_hw_hash=hash("""{"function_keys":333,"keyboard_subtype":222,"keyboard_type":111,"platform":"windows"}""")
keyboard_hash=hash("""{"OEMCP":444,"function_keys":333,"key_names":[{"extended":false,"keyname":"first","scancode":1001},{"extended":false,"keyname":"Second","scancode":2002},{"extended":true,"keyname":"THIRD","scancode":3003}],"keyboard_subtype":222,"keyboard_type":111,"oem_mapping":[1,2,3],"platform":"windows"}""")
physkey_keyname_dict={
	"_03E9": "first",
	"_07D2": "Second",
	"E0BBB": "THIRD"}
initmsg_out={**initmsg,
	"physkey_keyname_dict":physkey_keyname_dict,
	"keyboard_hash": keyboard_hash,
	"keyboard_hw_hash": keyboard_hw_hash}
testtransformation([enrich_input], "enrich_input",
	[initmsg,
	 {"type":"keydown"  ,"win_scancode": 1001,"win_virtualkey": 13,"win_extended":False},
	 {"type":"keyup"    ,"win_scancode": 2002,"win_virtualkey": 27,"win_extended":False},
	 {"type":"keypress" ,"win_scancode": 3003,"win_virtualkey": 65,"win_extended":False},
	 {"type":"keydown"  ,"win_scancode": 3003,"win_virtualkey": 65,"win_extended":True}],
	[[initmsg_out],
	 [{'type': 'keydown',  'win_scancode': 1001, 'win_virtualkey': 13,
	   'win_extended': False, 'physkey': '_03E9', 'keyid': '_03E9.0D',
	   'win_virtualkey_symbol': 'VK_RETURN', 'win_virtualkey_description': 'ENTER key',
	   'keyname_local': 'first'}],
	 [{'type': 'keyup',    'win_scancode': 2002, 'win_virtualkey': 27,
	   'win_extended': False, 'physkey': '_07D2', 'keyid': '_07D2.1B',
	   'win_virtualkey_symbol': 'VK_ESCAPE', 'win_virtualkey_description': 'ESC key',
	   'keyname_local': 'Second'}],
	 [{'type': 'keypress', 'win_scancode': 3003, 'win_virtualkey': 65,
	   'win_extended': False, 'physkey': '_0BBB', 'keyid': '_0BBB.41',
	   'win_virtualkey_symbol': None, 'win_virtualkey_description': 'A key'}],
	 [{'type': 'keydown',  'win_scancode': 3003, 'win_virtualkey': 65,
	   'win_extended': True,  'physkey': 'E0BBB', 'keyid': 'E0BBB.41',
	   'win_virtualkey_symbol': None, 'win_virtualkey_description': 'A key',
	   'keyname_local': 'THIRD'}]
	])

simple_chord=[
	{"type":"keydown","f": 1},
	{"type":"keydown","f": 2},
	{"type":"keyup"  ,"f": 2},
	{"type":"keyup"  ,"f": 1}]
not_chord=[
	{"type":"keydown","f": 1},
	{"type":"keydown","f": 2},
	{"type":"keyup"  ,"f": 1},
	{"type":"keyup"  ,"f": 2}]
leave_mods=[
	{"type":"keydown","f": 1},
	{"type":"keydown","f": 2},
	{"type":"keydown","f": 3},
	{"type":"keyup"  ,"f": 3},
	{"type":"keyup"  ,"f": 2},
	{"type":"keydown","f": 4},
	{"type":"keyup"  ,"f": 4},
	{"type":"keydown","f": 5},
	{"type":"keyup"  ,"f": 1},
	{"type":"keydown","f": 6},
	{"type":"keyup"  ,"f": 6},
	{"type":"keyup"  ,"f": 5}]
input=[*simple_chord, *not_chord, *leave_mods]
output=unchanged(input)
testtransformation([allow_repeat("f")], "allow_repeat 1", input, output)

repeat=[
	{"type":"keydown","f": 1},
	{"type":"keydown","f": 1},
	{"type":"keydown","f": 2},
	{"type":"keydown","f": 2},
	{"type":"keydown","f": 2},
	{"type":"keyup"  ,"f": 2},
	{"type":"keyup"  ,"f": 1}]
input=repeat
output=[
	[{"type":"keydown","f": 1}],
	[{"type":"keyup"  ,"f": 1}, {"type":"keydown","f": 1}],
	[{"type":"keydown","f": 2}],
	[{"type":"keyup"  ,"f": 2}, {"type":"keydown","f": 2}],
	[{"type":"keyup"  ,"f": 2}, {"type":"keydown","f": 2}],
	[{"type":"keyup"  ,"f": 2}],
	[{"type":"keyup"  ,"f": 1}]]
testtransformation([allow_repeat("f")], "allow_repeat 2", input, output)

testtransformation([events_to_chords("f")], "events_to_chords 1", simple_chord,
	[[],[],[{'type':'chord','chord':[1,2]}],[{'type':'keyup_all'}]])

testtransformation([events_to_chords("f")], "events_to_chords 2", not_chord,
	[[],[],[{'type':'chord','chord':[1]}],[{'type':'chord','chord':[2]},{'type':'keyup_all'}]])

testtransformation([events_to_chords("f")], "events_to_chords 3", leave_mods, [
	[],[],[],
	[{'type':'chord','chord':[1, 2, 3]}],
	[],[],
	[{'type':'chord','chord':[1, 4]}],
	[],[],[],
	[{'type':'chord','chord':[5, 6]}],
	[{'type':'keyup_all'}]])

testtransformation([events_to_chords("f")], "events_to_chords 4", repeat, [
	[],[],[],[],[],[{'type':'chord','chord':[1, 2]}],[{'type':'keyup_all'}]])

testtransformation([allow_repeat("f"), events_to_chords("f")], "events_to_chords 5", repeat, [
	[],[{'type':'chord','chord':[1]},{'type':'keyup_all'}],
	[],[{'type':'chord','chord':[1, 2]}],
	[{'type':'chord','chord':[1, 2]}],
	[{'type':'chord','chord':[1, 2]}],
	[{'type':'keyup_all'}]])

testtransformation([events_to_chords("f"), chords_to_events("f")], "chords_to_events 1",
	simple_chord,
	[[], [], [{'type': 'keydown', 'f': 1}, {'type': 'keypress', 'f': 2}],
	 [{'type': 'keyup', 'f': 1}, {'type': 'keyup_all'}]])

testtransformation([events_to_chords("f"), chords_to_events("f")], "chords_to_events 2",
	not_chord,
	[[], [], [{'type': 'keypress', 'f': 1}],
	 [{'type': 'keypress', 'f': 2}, {'type': 'keyup_all'}]])

testtransformation([events_to_chords("f"), chords_to_events("f")], "chords_to_events 3",
	leave_mods,
	[[],[],[],[{"type":"keydown" ,"f": 1},{"type":"keydown" ,"f": 2},{"type":"keypress","f": 3}],
	 [],[],   [{"type":"keyup"   ,"f": 2},{"type":"keypress","f": 4}],
	 [],[],[],[{"type":"keyup"   ,"f": 1},{"type":"keydown" ,"f": 5},{"type":"keypress","f": 6}],
	          [{"type":"keyup"   ,"f": 5},{'type': 'keyup_all'}]])

testtransformation([events_to_chords("f"), chords_to_events("f")], "chords_to_events 4",
	repeat,
	[[],[],[],[],[],[{"type":"keydown","f": 1},{"type":"keypress","f": 2}],
	 [{"type":"keyup"   ,"f": 1},{'type': 'keyup_all'}]])

testtransformation([allow_repeat("f"),events_to_chords("f"), chords_to_events("f")], "chords_to_events 5",
	repeat,
	[[],[{"type":"keypress","f": 1},{'type': 'keyup_all'}],
	 [],[{"type":"keydown","f": 1},{"type":"keypress","f": 2}],
	 [{"type":"keypress","f": 2}],
	 [{"type":"keypress","f": 2}],
	 [{"type":"keyup"   ,"f": 1},{'type': 'keyup_all'}]])

input=[
	{"type":"init"},
	{"type":"keydown"},
	{"type":"keyup"},
	{"type":"keypress"},
	{"type":"keydown", "unicode_codepoint":15},
	{"type":"keyup", "win_scancode":16},
	{"type":"keypress", "win_virtualkey":17},
	{"type":"illegal"},
	{"type":"chord"},
	{"type":"keyup_all"},
	{"type":"exit"},
	{"type":"keydown",
	 "win_scancode":  11111,
	 "win_virtualkey": 2222,
	 "win_extended":True},
	{"type":"keypress",
	 "win_scancode":    1,
	 "win_virtualkey": 27,
	 "win_extended":False,
	 "win_injected":False,
	 "win_lower_il_injected":False,
	 "win_altdown":False,
	 "win_time":1234567890,
	 "illegal":True}]
output=[
	[],
	[],
	[],
	[],
	[{"type":"keydown", "unicode_codepoint":15}],
	[{"type":"keyup", "win_scancode":16}],
	[{"type":"keypress", "win_virtualkey":17}],
	[],
	[],
	[],
	[],
	[{"type":"keydown",
	  "win_scancode":  11111,
	  "win_virtualkey": 2222,
	  "win_extended":True}],
	[{"type":"keypress",
	  "win_scancode":    1,
	  "win_virtualkey": 27}]]
testtransformation([sendkey_cleanup], "sendkey_cleanup", input, output)

output=[output[0],*[[e] for e in input[1:4]],*output[4:-1],[input[-1]]]
testtransformation([selecttypes(["keydown","keyup","keypress"])], "selecttypes", input, output)

testtransformation(
	[selecttypes(["keydown","keyup","keypress"]),
	 selectfields(["type", "win_scancode", "win_virtualkey", "win_extended", "unicode_codepoint"])],
	"selectfields", input[:-1], output[:-1])

testtransformation(
	[altgr_workaround_input, altgr_workaround_output],
	"altgr_workaround_input and altgr_workaround_output",
	[{"type":"keydown" ,"win_scancode":  541,"win_virtualkey":162,"win_extended":False,"win_injected":False,"win_lower_il_injected":False,"win_altdown":True ,"win_time":156},
	 {"type":"keydown" ,"win_scancode":   56,"win_virtualkey":165,"win_extended":True ,"win_injected":False,"win_lower_il_injected":False,"win_altdown":True ,"win_time":156},
	 {"type":"keyup"   ,"win_scancode":   56,"win_virtualkey":165,"win_extended":True ,"win_injected":False,"win_lower_il_injected":False,"win_altdown":False,"win_time":765},
	 {"type":"keydown" ,"win_virtualkey": 68},
	 {"type":"keypress","win_virtualkey":165},
	 {"type":"keyup"   ,"win_virtualkey": 68},
	 {"type":"keydown" ,"win_virtualkey":165},
	 {"type":"keypress","win_virtualkey": 68},
	 {"type":"keyup"   ,"win_virtualkey":165},
	 {"type":"keyup"   ,"win_scancode":  541,"win_virtualkey":162,"win_extended":False,"win_injected":False,"win_lower_il_injected":False,"win_altdown":False,"win_time":765}
	],
	[[],
	 [{"type":"keydown" ,"win_scancode":  541,"win_virtualkey":162,"win_extended":False,"win_time":156},
	  {"type":"keydown" ,"win_scancode":   56,"win_virtualkey":165,"win_extended":True ,"win_injected":False,"win_lower_il_injected":False,"win_altdown":True ,"win_time":156}],
	 [{"type":"keyup"   ,"win_scancode":  541,"win_virtualkey":162,"win_extended":False,"win_time":765},
	  {"type":"keyup"   ,"win_scancode":   56,"win_virtualkey":165,"win_extended":True ,"win_injected":False,"win_lower_il_injected":False,"win_altdown":False,"win_time":765}],
	 [{"type":"keydown" ,"win_virtualkey": 68}],
	 [{"type":"keydown" ,"win_virtualkey":162,"win_scancode":541,"win_extended":False},
	  {"type":"keydown" ,"win_virtualkey":165},
	  {"type":"keyup"   ,"win_virtualkey":162,"win_scancode":541,"win_extended":False},
	  {"type":"keyup"   ,"win_virtualkey":165}],
	 [{"type":"keyup"   ,"win_virtualkey": 68}],
	 [{"type":"keydown" ,"win_virtualkey":162,"win_scancode":541,"win_extended":False},
	  {"type":"keydown" ,"win_virtualkey":165}],
	 [{"type":"keypress","win_virtualkey": 68}],
	 [{"type":"keyup"   ,"win_virtualkey":162,"win_scancode":541,"win_extended":False},
	  {"type":"keyup"   ,"win_virtualkey":165}],
	 []])
