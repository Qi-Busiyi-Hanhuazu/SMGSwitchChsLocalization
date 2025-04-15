import struct


class Yaz0:
  @staticmethod
  def decompress(data: bytes, endianess: str = "<") -> bytes:
    magic = data[:4]
    if magic != b"Yaz0":
      raise ValueError("Invalid Yaz0 magic number")
    original_size, _1, _2 = struct.unpack_from(f"{endianess}III", data, 4)

    assert _1 == _2 == 0

    output = bytearray()
    src_pos = 0x10
    while len(output) < original_size:
      if src_pos >= len(data):
        raise ValueError("Source position exceeds data length")

      code_byte = data[src_pos]
      src_pos += 1

      for i in range(8):
        if len(output) >= original_size:
          break

        if code_byte & (1 << (7 - i)):
          output.append(data[src_pos])
          src_pos += 1
        else:
          if src_pos + 1 >= len(data):
            raise ValueError("Source position exceeds data length")

          (u16,) = struct.unpack_from(">H", data, src_pos)
          src_pos += 2
          dist = (u16 & 0xFFF) + 1
          copy_length = u16 >> 12

          if copy_length == 0:
            copy_length = data[src_pos] + 0x12
            src_pos += 1
          else:
            copy_length += 2

          for j in range(copy_length):
            output.append(output[-dist])
          if len(output) > original_size:
            raise ValueError("Output size exceeds original size")
    return bytes(output)


if __name__ == "__main__":
  with open("original_files/MessageData/Message.arc", "rb") as reader:
    data = reader.read()
    decompressed_data = Yaz0.decompress(data, ">")
    with open("decompressed.bin", "wb") as writer:
      writer.write(decompressed_data)
