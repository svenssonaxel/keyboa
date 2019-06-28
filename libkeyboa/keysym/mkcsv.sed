# Filter rows with keysyms
/^#define.*0x/!d;

# Convert to csv
s!^#define[[:space:]]+([[:alnum:]_]*XKB?_[[:alnum:]_]+)[[:space:]]+(0x[0-9A-Fa-f]+)([[:space:]]+/\*.*\*/ *)?$!\2,\1,\3!

# Remove /* comments */ and add quote
s!^([^,]+,[^,]+,)[[:space:]]*/\*[[:space:]]*!\1"!
s![[:space:]]*\*/[[:space:]]*$!"!

# Remove leading zeroes
s!^(0x)0+([0-9A-Fa-f]+,)!\1\2!

# Remove collisions:
/^0x100000EE,XKB_KEY_hpYdiaeresis,$/d

# Add column for Unicode codepoint
s!$!,!
s!^([^,]+,[^,]+,"U\+)([0-9A-Fa-f]+)([[:space:]].*",$)!\1\2\30x\2!

# Merge keysym names in XKB style
s/,XKB_KEY_/,/
s/,apXK_/,ap/
