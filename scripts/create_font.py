import json
import math
import os
import re
from typing import Callable, TypedDict

import brfnt
from helper import (
  DIR_FONT_EXTRACTED,
  DIR_FONT_IMPORT,
  DIR_HAR_EXTRACTED_FONT,
  DIR_HAR_REPLACE,
  convert_bytes_to_image,
  convert_image_to_bytes,
  get_blank_image,
)
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from xzonn_mt_tools.helper import TranslationItem


class FontConfig(TypedDict):
  size: int
  font: str
  draw: Callable[[ImageFont.FreeTypeFont, str, int | float], Image.Image]
  char_width: int
  char_length: int
  hash_map: list[str]


def draw_message_font(
  font: ImageFont.FreeTypeFont,
  char: str,
  scale_factor: int | float = 1,
) -> Image.Image:
  tile = Image.new("RGBA", (math.ceil(27 * scale_factor), math.ceil(33 * scale_factor)))
  draw = ImageDraw.Draw(tile)
  x, y = 0, 27
  draw.text(
    (x * scale_factor, y * scale_factor),
    char + "　　黑鼠龙龟",
    (0xFF, 0xFF, 0xFF),
    font,
    "ls",
  )
  return tile


def draw_cinema_font(
  font: ImageFont.FreeTypeFont,
  char: str,
  scale_factor: int | float = 1,
):
  tile = draw_message_font(font, char, scale_factor)
  tile = tile.filter(ImageFilter.GaussianBlur(round(1 * scale_factor)))
  return tile


def draw_menu_font(
  font: ImageFont.FreeTypeFont,
  char: str,
  scale_factor: int | float = 1,
) -> Image.Image:
  tile = Image.new("RGBA", (math.ceil(60 * scale_factor), math.ceil(64 * scale_factor)))
  draw = ImageDraw.Draw(tile)
  x, y = 3, 52
  draw.text(
    (x * scale_factor, y * scale_factor),
    char + "　　黑鼠龙龟",
    (0xFF, 0xFF, 0xFF),
    font,
    "ls",
    stroke_width=round(4 * scale_factor),
    stroke_fill=(0x00, 0x00, 0x00),
  )
  return tile


FONT_CONFIG: dict[str, FontConfig | None] = {
  "messagefont26": {
    "size": 27,
    "font": "files/fonts/DFFangYuanGB-W7.ttf",
    "draw": draw_message_font,
    "char_width": 26,
    "char_length": 26,
    "hash_map": [
      "917685881c23eb0c",
      "f32da07026559e14",
      "e3f50cf1a0bb03cd",
      "601c444240bcb3c",
      "7b1e35cbe19ca04d",
      "7b9bc0f35dd8f922",
    ],
  },
  "cinemafont26": {
    "size": 27,
    "font": "files/fonts/DFFangYuanGB-W7.ttf",
    "draw": draw_cinema_font,
    "char_width": 26,
    "char_length": 26,
    "hash_map": [],
  },
  "menufont64": {
    "size": 52,
    "font": "files/fonts/DFHaiBaoGB-W12.ttf",
    "draw": draw_menu_font,
    "char_width": 60,
    "char_length": 60,
    "hash_map": [
      "6562843e0fdea521",
      "e082f66aac302193",
      "3ca60e11abd6f23",
      "d4aa5628932f4898",
      "d988d71df0cd189a",
      "fe9b0e997866215f",
      "bdd880b72dce20e3",
      "90f78828b1920d5c",
      "4be165a186e2b5b",
      "332f022f9ec2c750",
      "87a31f2030085c48",
      "307875485383f9e3",
      "e5b7a7b02f028882",
    ],
  },
}


def filter_character(char: str):
  code = ord(char)
  if code <= 0x80 or 0x2000 <= code <= 0x206F or 0x2600 <= code <= 0x26FF or 0x3000 <= code <= 0x303F or code >= 0xFF00:
    return True
  if code == 0x30FB:
    return True
  return False


def replace_font(
  font: brfnt.BRFNT,
  font_config: FontConfig,
  characters: set[str],
  texture_input_root: str = "",
  texture_output_root: str = "",
  scale_factor: int | float = 1,
) -> None:
  old_characters = filter(filter_character, map(chr, font.char_map.values()))
  new_characters = set(old_characters) | characters

  image_width = font.tglp.image_width
  image_height = font.tglp.image_height
  image_format = font.tglp.image_format
  cell_width = font.tglp.cell_width + 1
  cell_height = font.tglp.cell_height + 1
  char_per_image = font.tglp.cells_per_column * font.tglp.cells_per_row

  old_tile_images: list[Image.Image] = []

  if texture_input_root == "":
    for tile_data in font.tglp.image_data:
      old_tile_images.append(convert_bytes_to_image(tile_data, image_width, image_height, image_format))
  else:
    for path in font_config["hash_map"]:
      old_tile_images.append(Image.open(f"{texture_input_root}/{path}.png"))

  old_index_map = {v: k for k, v in font.char_map.items()}
  old_char_map = font.char_map

  new_tiles: list[Image.Image] = []
  new_char_codes: list[int] = []
  new_cwdh_info: list[brfnt.CWDHInfo] = []

  ttf = ImageFont.truetype(font_config["font"], font_config["size"] * scale_factor)

  for char in sorted(new_characters):
    char_code = ord(char)
    if char_code in old_index_map and (char_code == ord("辻") or not 0x4E00 <= char_code <= 0x9FFF):
      old_index = old_index_map[char_code]
      old_image_index = old_index // char_per_image
      old_image = old_tile_images[old_image_index]
      y = old_index % char_per_image // font.tglp.cells_per_row
      x = old_index % font.tglp.cells_per_row
      new_tiles.append(
        old_image.crop(
          (
            x * cell_width * scale_factor,
            y * cell_height * scale_factor,
            (x + 1) * cell_width * scale_factor,
            (y + 1) * cell_height * scale_factor,
          )
        )
      )
      new_char_codes.append(char_code)
      new_cwdh_info.append(font.cwdhs[0].info[old_index])
    else:
      new_image = font_config["draw"](ttf, char, scale_factor)
      new_tiles.append(new_image)
      new_char_codes.append(char_code)
      new_cwdh_info.append(
        brfnt.CWDHInfo(
          font.finf.default_start,
          font_config.get("char_width", font.finf.default_width),
          font_config.get("char_length", font.finf.default_length),
        )
      )

  new_char_map = dict(zip(range(len(new_char_codes)), new_char_codes))
  font.cmaps = brfnt.BRFNT.compress_cmap(new_char_map)
  font.char_map = new_char_map
  font.cwdhs[0].info = new_cwdh_info
  font.cwdhs[0].last_index = len(new_tiles)
  new_images = [
    get_blank_image(round(image_width * scale_factor), round(image_height * scale_factor), image_format)
    for _ in range(math.ceil(len(new_tiles) / char_per_image))
  ]

  for index, char in new_char_map.items():
    image_index = index // char_per_image
    y = index % char_per_image // font.tglp.cells_per_row
    x = index % font.tglp.cells_per_row
    new_images[image_index].paste(
      new_tiles[index], (round(x * cell_width * scale_factor), round(y * cell_height * scale_factor))
    )

  if texture_output_root == "":
    font.tglp.image_data = [convert_image_to_bytes(image, image_format) for image in new_images]
  else:
    os.makedirs(texture_output_root, exist_ok=True)
    for index, image in enumerate(new_images):
      image.save(f"{texture_output_root}/{font_config['hash_map'][index]}.png")

  font.tglp.image_count = len(new_images)


def get_characters(key_list: list[str] = []) -> set[str]:
  characters = set()
  CONTROL_PATTERN = re.compile(r"\[[^\[\]]+\]")
  with open("texts/zh_Hans/nsw/messages.json", "r", -1, "utf8") as reader:
    translation_list: list[TranslationItem] = json.load(reader)

  for translation in translation_list:
    if key_list and translation["key"] not in key_list:
      continue
    text = translation["translation"]
    text = CONTROL_PATTERN.sub("", text)
    text = text.replace("\n", "").replace("\\f", "")
    for char in text:
      code = ord(char)
      if 0x4E00 <= code <= 0x9FFF:
        characters.add(char)
      if 0x2000 <= code <= 0x206F or 0x2600 <= code <= 0x26FF or 0x3000 <= code <= 0x303F or 0xFF00 <= code <= 0xFFEF:
        characters.add(char)

  return characters


if __name__ == "__main__":
  full_characters = get_characters()
  for font_name, font_config in FONT_CONFIG.items():
    if os.path.exists(f"files/fonts/keys_{font_name}.txt"):
      with open(f"files/fonts/keys_{font_name}.txt") as reader:
        characters = get_characters(reader.read().splitlines())
    else:
      characters = full_characters
    with open(f"{DIR_FONT_EXTRACTED}/{font_name}.brfnt", "rb") as reader:
      font = brfnt.BRFNT(reader.read())

    if font_config is not None:
      if font_config["hash_map"]:
        replace_font(font, font_config, characters, DIR_HAR_EXTRACTED_FONT, DIR_HAR_REPLACE, 2.4)
      else:
        replace_font(font, font_config, characters)

    output_path = f"{DIR_FONT_IMPORT}/{font_name}.brfnt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as writer:
      writer.write(font.get_bytes("<", "<"))
