import re

WII_CONTROL_REPLACER = {
  re.compile(r"\[1:0001\]"): r"\\f",
  re.compile(r"\[1:0002\]"): r"[unk1]",
  re.compile(r"\[1:0000([0-9a-f]{2})([0-9a-f]{2})\]"): r"[wait:\1\2]",
  re.compile(r"\[3:([0-9a-f]{2})([0-9a-f]{2})\]"): r"[icon:\1\2]",
  re.compile(r"\[4:([0-9a-f]{2})([0-9a-f]{2})\]"): r"[unk4:\1\2]",
  re.compile(r"\[5:0000([0-9a-f]{2})00\]"): r"[unk5:\1]",
  re.compile(
    r"\[6:([0-9a-f]{2})([0-9a-f]{2})00000000([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})\]"
  ): r"[placeholder6:\1\2,\3\4\5\6]",
  re.compile(
    r"\[7:([0-9a-f]{2})([0-9a-f]{2})00000000([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})\]"
  ): r"[placeholder7:\1\2,\3\4\5\6]",
  re.compile(r"\[9:([0-9a-f]{2})([0-9a-f]{2})\]"): r"[unk9:\1\2]",
  re.compile(r"\[255:0000([0-9a-f]{2})00\]"): r"[color:\1]",
  re.compile(r"\[255:0002[0-9a-f]+\]"): "",
}
NSW_CONTROL_REPLACER = {
  re.compile(r"\[1:0100\]"): r"\\f",
  re.compile(r"\[1:0200\]"): r"[unk1]",
  re.compile(r"\[1:0000([0-9a-f]{2})([0-9a-f]{2})\]"): r"[wait:\2\1]",
  re.compile(r"\[3:([0-9a-f]{2})([0-9a-f]{2})\]"): r"[icon:\2\1]",
  re.compile(r"\[4:([0-9a-f]{2})([0-9a-f]{2})\]"): r"[unk4:\2\1]",
  re.compile(r"\[5:0000([0-9a-f]{2})00\]"): r"[unk5:\1]",
  re.compile(
    r"\[6:([0-9a-f]{2})([0-9a-f]{2})00000000([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})\]"
  ): r"[placeholder6:\2\1,\6\5\4\3]",
  re.compile(
    r"\[7:([0-9a-f]{2})([0-9a-f]{2})00000000([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})\]"
  ): r"[placeholder7:\2\1,\6\5\4\3]",
  re.compile(r"\[9:([0-9a-f]{2})([0-9a-f]{2})\]"): r"[unk9:\2\1]",
  re.compile(r"\[255:0000([0-9a-f]{2})00\]"): r"[color:\1]",
  re.compile(r"\[255:0200[0-9a-f]+\]"): "",
}
CONTROL_REPLACERS = {
  "wii": WII_CONTROL_REPLACER,
  "nsw": NSW_CONTROL_REPLACER,
}
