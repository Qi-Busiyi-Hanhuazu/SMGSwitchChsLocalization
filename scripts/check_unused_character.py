import json
import re

from xzonn_mt_tools.helper import TranslationItem

unused_characters = set()

with open("out/characters/messagefont26.txt", "r", -1, "utf8") as reader:
  characters = set(reader.read())

CONTROL_PATTERN = re.compile(r"\[[^\[\]]+\]")
with open("texts/zh_Hans/nsw/messages.json", "r", -1, "utf8") as reader:
  translation_list: list[TranslationItem] = json.load(reader)

for translation in translation_list:
  text = translation["translation"]
  text = CONTROL_PATTERN.sub("", text)
  text = text.replace("\n", "").replace("\\f", "")
  for character in text:
    if character in characters:
      continue
    if character not in unused_characters:
      print(f"Unused character: {character}")
      unused_characters.add(character)
