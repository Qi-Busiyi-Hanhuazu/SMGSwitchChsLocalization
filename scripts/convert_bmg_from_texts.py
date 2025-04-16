import json
import os
import re

import bmg
from xzonn_mt_tools.helper import TranslationItem

NSW_CONTROL_COVERTER = {
  re.compile(r"\\f"): r"[1:0100]",
  re.compile(r"\[unk1\]"): r"[1:0200]",
  re.compile(r"\[wait:([0-9a-f]{2})([0-9a-f]{2})\]"): r"[1:0000\2\1]",
  re.compile(r"\[icon:([0-9a-f]{2})([0-9a-f]{2})\]"): r"[3:\2\1]",
  re.compile(r"\[unk4:([0-9a-f]{2})([0-9a-f]{2})\]"): r"[4:\2\1]",
  re.compile(r"\[unk5:([0-9a-f]{2})\]"): r"[5:0000\g<1>00]",
  re.compile(
    r"\[placeholder6:([0-9a-f]{2})([0-9a-f]{2}),([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})\]"
  ): r"[6:\2\g<1>00000000\6\5\4\3]",
  re.compile(
    r"\[placeholder7:([0-9a-f]{2})([0-9a-f]{2}),([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})\]"
  ): r"[7:\2\g<1>00000000\6\5\4\3]",
  re.compile(r"\[unk9:([0-9a-f]{2})([0-9a-f]{2})\]"): r"[9:\2\1]",
  re.compile(r"\[color:([0-9a-f]{2})\]"): r"[255:0000\g<1>00]",
}

with open("texts/ja/nsw/messages.json", "r", -1, "utf8") as reader:
  ja_items: list[TranslationItem] = json.load(reader)


with open("texts/zh_Hans/nsw/messages.json", "r", -1, "utf8") as reader:
  zh_items: list[TranslationItem] = json.load(reader)
zh_dict = {item["key"]: item for item in zh_items}
translated_items = ja_items
for item in translated_items:
  key = item["key"]
  if key in zh_dict:
    item["translation"] = zh_dict[key]["translation"]


with open("unpacked/nsw/Message/message.bmg", "rb") as reader:
  bmg_file = bmg.BMG(reader.read())


assert len(bmg_file.messages) == len(translated_items)
for i, message in enumerate(bmg_file.messages):
  text = translated_items[i]["translation"]
  if text == "":
    continue

  for pattern, replacement in NSW_CONTROL_COVERTER.items():
    text = pattern.sub(replacement, text)

  string_parts = []
  char_pos = 0
  while char_pos < len(text):
    char = text[char_pos]
    if char != "[":
      string_parts.append(char)
      char_pos += 1
      continue

    control_end = text.find("]", char_pos)
    if control_end == -1:
      raise ValueError(f"Missing closing bracket in {text}")

    control_type, control_data = text[char_pos + 1 : control_end].split(":", 1)
    string_parts.append(bmg.Message.Escape(int(control_type), bytes.fromhex(control_data)))
    char_pos = control_end + 1

  message.stringParts = string_parts


output_path = "temp/import/Message/message.bmg"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "wb") as writer:
  writer.write(bmg_file.save())
