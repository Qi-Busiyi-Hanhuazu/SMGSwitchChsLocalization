import os

import brfnt

FONTS = {
  "cinemafont26.brfnt": 0,
  "menufont64.brfnt": 1,
  "messagefont26.brfnt": 2,
}

for key, value in FONTS.items():
  with open(f"unpacked/wii_cn/Font/{key}", "rb") as reader:
    font = brfnt.BRFNT(reader.read())

  output_path = f"out/characters/{key.removesuffix('.brfnt')}.txt"
  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  with open(output_path, "w", -1, "utf8") as writer:
    characters = sorted(map(chr, font.char_map.values()))
    writer.write("".join(characters))

  output_path = f"temp/import/Font/{key}"
  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  with open(output_path, "wb") as writer:
    writer.write(font.get_bytes("<", "<"))
