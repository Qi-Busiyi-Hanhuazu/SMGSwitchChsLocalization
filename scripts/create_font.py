import json
import math
import os
import re
from typing import Callable, TypedDict

import brfnt
from helper import convert_bytes_to_image, convert_image_to_bytes, get_blank_image
from PIL import Image, ImageDraw, ImageFont
from xzonn_mt_tools.helper import TranslationItem


class FontConfig(TypedDict):
  size: int
  font: str
  draw: Callable[[ImageFont.FreeTypeFont, str], Image.Image]


def draw_message_font(font: ImageFont.FreeTypeFont, char: str) -> Image.Image:
  tile = Image.new("L", (27, 27))
  draw = ImageDraw.Draw(tile)
  x, y = 0, 23
  draw.text(
    (x, y),
    char + "　　黑鼠龙龟",
    0xFF,
    font,
    "ls",
  )
  return tile


FONT_CONFIG: dict[str, FontConfig | None] = {
  "messagefont26.brfnt": {
    "size": 26,
    "font": "files/fonts/DFFangYuanGB-W7.ttf",
    "draw": draw_message_font,
  },
  "cinemafont26.brfnt": None,
  "menufont64.brfnt": None,
}


def replace_font(font: brfnt.BRFNT, font_name: str, font_config: FontConfig) -> None:
  old_characters = sorted(map(chr, font.char_map.values()))
  new_characters = set(old_characters) | characters

  image_width = font.tglp.image_width
  image_height = font.tglp.image_height
  image_format = font.tglp.image_format
  cell_width = font.tglp.cell_width + 1
  cell_height = font.tglp.cell_height + 1
  char_per_image = font.tglp.cells_per_column * font.tglp.cells_per_row

  old_tile_images = [
    convert_bytes_to_image(tile_data, image_width, image_height, image_format) for tile_data in font.tglp.image_data
  ]
  old_index_map = {v: k for k, v in font.char_map.items()}
  old_char_map = font.char_map

  new_tiles: list[Image.Image] = []
  new_char_codes: list[int] = []
  new_cwdh_info: list[brfnt.CWDHInfo] = []

  ttf = ImageFont.truetype(font_config["font"], font_config["size"])

  for char in sorted(new_characters):
    char_code = ord(char)
    if char_code == ord("辻") or not 0x4E00 <= char_code <= 0x9FFF:
      old_index = old_index_map[char_code]
      old_image_index = old_index // char_per_image
      old_image = old_tile_images[old_image_index]
      y = old_index % char_per_image // font.tglp.cells_per_row
      x = old_index % font.tglp.cells_per_row
      new_tiles.append(
        old_image.crop(
          (
            x * cell_width,
            y * cell_height,
            (x + 1) * cell_width,
            (y + 1) * cell_height,
          )
        )
      )
      new_char_codes.append(char_code)
      new_cwdh_info.append(font.cwdhs[0].info[old_index])
    else:
      new_image = font_config["draw"](ttf, char)
      new_tiles.append(new_image)
      new_char_codes.append(char_code)
      new_cwdh_info.append(brfnt.CWDHInfo(font.finf.default_start, font.finf.default_width, font.finf.default_length))

  new_char_map = dict(zip(range(len(new_char_codes)), new_char_codes))
  font.cmaps = brfnt.BRFNT.compress_cmap(new_char_map)
  font.char_map = new_char_map
  font.cwdhs[0].info = new_cwdh_info
  new_images = [
    get_blank_image(image_width, image_height, image_format) for _ in range(math.ceil(len(new_tiles) / char_per_image))
  ]

  for index, char in new_char_map.items():
    image_index = index // char_per_image
    y = index % char_per_image // font.tglp.cells_per_row
    x = index % font.tglp.cells_per_row
    new_images[image_index].paste(new_tiles[index], (x * cell_width, y * cell_height))

  font.tglp.image_data = [convert_image_to_bytes(image, image_format) for image in new_images]
  font.tglp.image_count = len(new_images)


def get_characters() -> set[str]:
  characters = set()
  CONTROL_PATTERN = re.compile(r"\[[^\[\]]+\]")
  with open("texts/zh_Hans/nsw/messages.json", "r", -1, "utf8") as reader:
    translation_list: list[TranslationItem] = json.load(reader)

  for translation in translation_list:
    text = translation["translation"]
    text = CONTROL_PATTERN.sub("", text)
    text = text.replace("\n", "").replace("\\f", "")
    for character in text:
      if 0x4E00 <= ord(character) <= 0x9FFF:
        characters.add(character)

  return characters


characters = get_characters()
for font_name, font_config in FONT_CONFIG.items():
  with open(f"unpacked/wii_cn/Font/{font_name}", "rb") as reader:
    font = brfnt.BRFNT(reader.read())

  if font_config is not None:
    replace_font(font, font_name, font_config)

  output_path = f"temp/import/Font/{font_name}"
  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  with open(output_path, "wb") as writer:
    writer.write(font.get_bytes("<", "<"))
