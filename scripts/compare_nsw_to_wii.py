import json
import os
import re

from xzonn_mt_tools.helper import TranslationItem

WII_RUBY_PATTERN = re.compile(r"\[255:0002[0-9a-f]+\]")
NSW_RUBY_PATTERN = re.compile(r"\[255:0200[0-9a-f]+\]")
CONTROL_PATTERN = re.compile(r"\[\d+:[0-9a-f]+\]")
wii_control_to_nsw = {}
different_key = set()

with open("texts/ja/wii/messages.json", "r", -1, "utf8") as reader:
  wii: list[TranslationItem] = json.load(reader)

wii_dict = {_["key"]: _ for _ in wii}

with open("texts/ja/nsw/messages.json", "r", -1, "utf8") as reader:
  nsw: list[TranslationItem] = json.load(reader)

nsw_dict = {_["key"]: _ for _ in nsw}

with open("texts/zh_Hans/wii/messages.json", "r", -1, "utf8") as reader:
  chs: list[TranslationItem] = json.load(reader)

chs_dict = {_["key"]: _ for _ in chs}

for key, item in nsw_dict.items():
  nsw_text = item["original"]
  if not nsw_text:
    continue
  if key not in wii_dict:
    print(f"Key {key} not found in Wii")
    continue
  wii_item = wii_dict[key]
  wii_text = wii_item["original"]

  wii_text = WII_RUBY_PATTERN.sub("", wii_text)
  nsw_text = NSW_RUBY_PATTERN.sub("", nsw_text)

  wii_controls = CONTROL_PATTERN.findall(wii_text)
  nsw_controls = CONTROL_PATTERN.findall(nsw_text)

  wii_text_without_controls = CONTROL_PATTERN.split(wii_text)
  nsw_text_without_controls = CONTROL_PATTERN.split(nsw_text)

  if wii_text_without_controls == nsw_text_without_controls:
    assert len(wii_controls) == len(nsw_controls)
    for wii_control, nsw_control in zip(wii_controls, nsw_controls):
      if wii_control not in wii_control_to_nsw:
        wii_control_to_nsw[wii_control] = nsw_control
      else:
        if nsw_control != wii_control_to_nsw[wii_control]:
          print(f"Control {wii_control} has different values: {wii_control_to_nsw[wii_control]} and {nsw_control}")
          continue
    continue

  different_key.add(key)

output = []
for key, item in nsw_dict.items():
  key = item["key"]
  text = item["original"]
  translated = False

  if key in chs_dict:
    text = chs_dict[key]["translation"]
    translated = True

    controls = CONTROL_PATTERN.findall(text)
    for control in controls:
      if control in wii_control_to_nsw:
        text = text.replace(control, wii_control_to_nsw[control], 1)
      else:
        print(f"Control {control} not found in wii_control_to_nsw")
        translated = False

  if key in different_key:
    translated = False

  new_item: TranslationItem = {
    "key": key,
    "original": item["original"],
    "translation": text,
  }
  if not translated:
    new_item["untranslated"] = True

  output.append(new_item)

os.makedirs("texts/zh_Hans/nsw", exist_ok=True)
with open("texts/zh_Hans/nsw/messages.json", "w", -1, "utf8") as writer:
  json.dump(output, writer, indent=2, ensure_ascii=False)
