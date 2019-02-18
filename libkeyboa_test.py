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
		print("Test FAILED: " + str(title))
		print("Expected output: " + str(output))
		print("Actual output: " + str(state))
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

testtransformation([enrich_input], "enrich_input",
	[{"type":"init","platform":"windows","key_names":[
		{"scancode":1001,"extended":False,"keyname":"first"},
		{"scancode":2002,"extended":False,"keyname":"Second"},
		{"scancode":3003,"extended":True,"keyname":"THIRD"}]},
	 {"type":"keydown"  ,"win_scancode": 1001,"win_virtualkey": 13,"win_extended":False},
	 {"type":"keyup"    ,"win_scancode": 2002,"win_virtualkey": 27,"win_extended":False},
	 {"type":"keypress" ,"win_scancode": 3003,"win_virtualkey": 65,"win_extended":False},
	 {"type":"keydown"  ,"win_scancode": 3003,"win_virtualkey": 65,"win_extended":True}],
	[[{"type":"init","platform":"windows","key_names":[
	  {"scancode":1001,"extended":False,"keyname":"first"},
	  {"scancode":2002,"extended":False,"keyname":"Second"},
	  {"scancode":3003,"extended":True,"keyname":"THIRD"}]}],
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
	[{"type":"keydown"}],
	[{"type":"keyup"}],
	[{"type":"keypress"}],
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

testtransformation([selecttypes(["keydown","keyup","keypress"])], "selecttypes", input[:-2], output[:-2])

testtransformation(
	[selecttypes(["keydown","keyup","keypress"]),
	 selectfields(["type", "win_scancode", "win_virtualkey", "win_extended"])],
	"selectfields", input[:-1], output[:-1])
