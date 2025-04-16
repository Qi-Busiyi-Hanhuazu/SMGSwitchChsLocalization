import re

from PIL import Image

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
  image = Image.new("L", (width, height))
  offset = 0
  for y in range(0, height, 8):
    for x in range(0, width, 8):
      block = data[offset : offset + 32]
      offset += 32
      half_bytes = bytearray()
      for byte in block:
        half_bytes.append((byte >> 4) << 4)
        half_bytes.append((byte & 0x0F) << 4)

      tile = Image.frombytes("L", (8, 8), half_bytes)
      image.paste(tile, (x, y))

  return image


def encode_a4_image(image: Image.Image) -> bytes:
  # A4
  width, height = image.size
  data = bytearray()
  for y in range(0, height, 8):
    for x in range(0, width, 8):
      tile = image.crop((x, y, x + 8, y + 8))
      half_bytes = tile.tobytes()
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
        i = (rgba_bytes[i] >> 4)
        data.append(a | i)

  return bytes(data)

def convert_bytes_to_image(data: bytes, width: int, height: int, format: int) -> Image.Image:
  if format == 0:
    return decode_i4_image(data, width, height)
  elif format == 2:
    return decode_ia4_image(data, width, height)
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
    return Image.new("L", (width, height))
  elif format == 2:
    return Image.new("RGBA", (width, height))
  else:
    raise NotImplementedError(f"Image format {format} not supported")
