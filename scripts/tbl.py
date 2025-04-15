import struct


class Tbl:
  def __init__(self, data: bytes):
    (dataLenLE,) = struct.unpack_from("<I", data, 0)
    (dataLenBE,) = struct.unpack_from(">I", data, 0)

    self.endianness = "<" if dataLenLE < dataLenBE else ">"

    (count, _1, header_size) = struct.unpack_from(f"{self.endianness}III", data, 0)
    self.table = []
    str_start = count * 0x08 + header_size
    for i in range(count):
      index, str_offset = struct.unpack_from(f"{self.endianness}II", data, header_size + i * 0x08)
      assert index == i
      string = data[str_start + str_offset : data.find(b"\0", str_start + str_offset)]
      self.table.append(string.decode())
