import struct


class RarcFile:
  def __init__(self, name: str, header_offset: int, data: bytes):
    self.name = name
    self.header_offset = header_offset
    self.data = data


class Rarc:
  def __init__(self, data: bytes):
    self.data = data
    self.files: list[RarcFile] = []

    magic = data[:4]
    if magic == b"RARC":
      endianess = ">"
    elif magic == b"CRAR":
      endianess = "<"
    else:
      raise ValueError("Invalid RARC magic number")

    self.endianess = endianess

    file_size, header_size, data_offset, data_size, unk_1, _2, _3 = struct.unpack_from(f"{endianess}IIIIIII", data, 4)
    assert data_size == unk_1

    node_count, node_offset, dir_count, dir_offset, fnt_size, fnt_offset, file_count, unk_1, _1 = struct.unpack_from(
      f"{endianess}IIIIIIHHI", data, 0x20
    )

    assert node_count == 1

    node_magic, node_name_offset, name_hash, dir_count_in_node, index = struct.unpack_from(
      f"{endianess}4sIHHI", data, node_offset + header_size
    )

    dirs = []
    offset = dir_offset + header_size
    for i in range(dir_count):
      index, name_hash, temp_1, file_offset, file_length, _1 = struct.unpack_from(f"{endianess}HHIIII", data, offset)
      file_name_offset = temp_1 & 0xFFFFFF
      file_type = temp_1 >> 24
      file_name = data[
        fnt_offset + file_name_offset + header_size : data.find(b"\0", fnt_offset + file_name_offset + header_size)
      ].decode()

      if file_name in (".", ".."):
        continue

      file = RarcFile(
        file_name,
        offset,
        data[data_offset + file_offset + header_size : data_offset + file_offset + header_size + file_length],
      )
      self.files.append(file)
      offset += 0x14

  def save(self) -> bytes:
    file_size, header_size, data_offset, data_size, unk_1, _2, _3 = struct.unpack_from(
      f"{self.endianess}IIIIIII", self.data, 4
    )
    assert data_size == unk_1
    output = bytearray(self.data[: data_offset + header_size])
    offset = 0
    for file in self.files:
      output[file.header_offset + 0x08 : file.header_offset + 0x10] = struct.pack(
        f"{self.endianess}II", offset, len(file.data)
      )
      zeros = b"\0" * ((0x20 - len(file.data) % 0x20) % 0x20)
      output += file.data + zeros
      offset += len(file.data) + len(zeros)

    return bytes(output)


if __name__ == "__main__":
  with open("decompressed.bin", "rb") as reader:
    rarc = Rarc(reader.read())

  for file in rarc.files:
    with open(file.name, "wb") as writer:
      writer.write(file.data)
