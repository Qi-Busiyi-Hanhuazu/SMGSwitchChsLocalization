import json
import os
import re

from bmg import BMG
from helper import CONTROL_REPLACERS
from tbl import Tbl

FILE_LIST = {
  "nsw": {
    "lang": "ja",
    "platform": "nsw",
  },
  "wii": {
    "lang": "ja",
    "platform": "wii",
  },
  "wii_cn": {
    "lang": "zh_Hans",
    "platform": "wii",
  },
}

for folder, config in FILE_LIST.items():
  input_folder = f"unpacked/{folder}/Message"
  control_replacer = CONTROL_REPLACERS[config["platform"]]

  bmg = BMG.fromFile(f"{input_folder}/message.bmg")
  with open(f"{input_folder}/messageid.tbl", "rb") as reader:
    tbl = Tbl(reader.read())

  output = []
  for i, message in enumerate(bmg.messages):
    text = str(message)
    for pattern, replacement in control_replacer.items():
      text = pattern.sub(replacement, text)

    item = {
      "index": i,
      "key": tbl.table[i],
      "original": text,
      "translation": text,
    }
    if not text.strip():
      item["trash"] = True

    output.append(item)

  output_path = f"texts/{config['lang']}/{config['platform']}/messages.json"
  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  with open(output_path, "w", -1, "utf8") as writer:
    json.dump(output, writer, ensure_ascii=False, indent=2)
