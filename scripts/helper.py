import re

from PIL import Image

DIR_ORIGINAL_FILES = "original_files"
DIR_ORIGINAL_FILES_NSW = f"{DIR_ORIGINAL_FILES}/nsw"
DIR_ORIGINAL_FILES_WII = f"{DIR_ORIGINAL_FILES}/wii"

DIR_HAR = "data/texture_replace"
DIR_HAR_EXTRACTED = "unpacked/texture_replace"
DIR_HAR_EXTRACTED_FONT = f"{DIR_HAR_EXTRACTED}/MarioGalaxy_ja"
DIR_HAR_REPLACE = "temp/texture_replace"

DIR_FONT_EXTRACTED = "unpacked/nsw/Font"
DIR_FONT_IMPORT = "temp/import/Font"

DIR_OUT = "out/010049900f546003/romfs"

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


def decode_i4_image(data: bytes, width: int, height: int):
  # I4
  image = Image.new("RGBA", (width, height))
  offset = 0
  for y in range(0, height, 8):
    for x in range(0, width, 8):
      block = data[offset : offset + 32]
      offset += 32
      rgba_bytes = bytearray()
      for byte in block:
        rgba_bytes.extend((0xFF, 0xFF, 0xFF, (byte >> 4) << 4))
        rgba_bytes.extend((0xFF, 0xFF, 0xFF, (byte & 0x0F) << 4))

      tile = Image.frombytes("RGBA", (8, 8), rgba_bytes)
      image.paste(tile, (x, y))

  return image


def encode_a4_image(image: Image.Image) -> bytes:
  # A4
  width, height = image.size
  data = bytearray()
  for y in range(0, height, 8):
    for x in range(0, width, 8):
      tile = image.crop((x, y, x + 8, y + 8))
      half_bytes = tile.getchannel("A").tobytes()
      for i in range(0, len(half_bytes), 2):
        byte = ((half_bytes[i] >> 4) << 4) | (half_bytes[i + 1] >> 4)
        data.append(byte)

  return bytes(data)


def decode_ia4_image(data: bytes, width: int, height: int):
  # IA4
  image = Image.new("RGBA", (width, height))
  offset = 0
  for y in range(0, height, 4):
    for x in range(0, width, 8):
      block = data[offset : offset + 32]
      offset += 32
      rgba_bytes = bytearray()
      for byte in block:
        i = (byte & 0x0F) << 4
        a = (byte >> 4) << 4
        rgba_bytes.extend((i, i, i, a))

      tile = Image.frombytes("RGBA", (8, 4), rgba_bytes)
      image.paste(tile, (x, y))

  return image


def encode_ia4_image(image: Image.Image) -> bytes:
  # IA4
  width, height = image.size
  data = bytearray()
  for y in range(0, height, 4):
    for x in range(0, width, 8):
      tile = image.crop((x, y, x + 8, y + 4))
      rgba_bytes = tile.tobytes()
      for i in range(0, len(rgba_bytes), 4):
        a = (rgba_bytes[i + 3] >> 4) << 4
        i = rgba_bytes[i] >> 4
        data.append(a | i)

  return bytes(data)


def decode_rgb5a3_image(data: bytes, width: int, height: int):
  # RGB5A3
  image = Image.new("RGBA", (width, height))
  offset = 0
  for y in range(0, height, 4):
    for x in range(0, width, 4):
      block = data[offset : offset + 32]
      offset += 32
      rgba_bytes = bytearray()
      for i in range(0, len(block), 2):
        word = int.from_bytes(block[i : i + 2], "big")
        top_bit = (word >> 15) & 0x01
        if top_bit == 0:
          r = ((word >> 8) & 0x0F) << 4
          g = ((word >> 4) & 0x0F) << 4
          b = (word & 0x0F) << 4
          a = ((word >> 12) & 0x07) << 5
        else:
          r = ((word >> 10) & 0x1F) << 3
          g = ((word >> 5) & 0x1F) << 3
          b = (word & 0x1F) << 3
          a = 0xFF

        rgba_bytes.extend((r, g, b, a))

      tile = Image.frombytes("RGBA", (4, 4), rgba_bytes)
      image.paste(tile, (x, y))

  return image


def convert_bytes_to_image(data: bytes, width: int, height: int, format: int) -> Image.Image:
  if format == 0:
    return decode_i4_image(data, width, height)
  elif format == 2:
    return decode_ia4_image(data, width, height)
  elif format == 5:
    return decode_rgb5a3_image(data, width, height)
  else:
    raise NotImplementedError(f"Image format {format} not supported")


def convert_image_to_bytes(image: Image.Image, format: int) -> bytes:
  if format == 0:
    return encode_a4_image(image)
  elif format == 2:
    return encode_ia4_image(image)
  else:
    raise NotImplementedError(f"Image format {format} not supported")


def get_blank_image(width: int, height: int, format: int) -> Image.Image:
  if format == 0:
    return Image.new("RGBA", (width, height))
  elif format == 2:
    return Image.new("RGBA", (width, height))
  else:
    raise NotImplementedError(f"Image format {format} not supported")
