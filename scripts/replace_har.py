import os
import struct

from helper import DIR_HAR, DIR_HAR_REPLACE, DIR_ORIGINAL_FILES_NSW, DIR_OUT


def replace_har(input_root: str, replace_root: str, output_root: str):
  for file_name in os.listdir(input_root):
    if not file_name.endswith(".har"):
      continue
    har_path = f"{input_root}/{file_name}"
    hix_path = f"{input_root}/{file_name.removesuffix('.har')}.hix"
    if not os.path.exists(hix_path):
      continue

    har_reader = open(har_path, "rb")
    hix_reader = open(hix_path, "rb")

    har_output_path = f"{output_root}/{file_name}"
    hix_output_path = f"{output_root}/{file_name.removesuffix('.har')}.hix"
    os.makedirs(os.path.dirname(har_output_path), exist_ok=True)

    har_writer = open(har_output_path, "wb")
    hix_writer = open(hix_output_path, "wb")

    hix_magic, hix_file_file_count = struct.unpack("<4sI", hix_reader.read(8))
    assert hix_magic == b"HIDX"
    hix_writer.write(struct.pack("<4sI", hix_magic, hix_file_file_count))

    har_magic, har_file_count, file_size = struct.unpack("<4sII", har_reader.read(12))
    assert har_magic == b"HARC"
    har_writer.write(struct.pack("<4sII", har_magic, har_file_count, file_size))

    assert hix_file_file_count == har_file_count

    for i in range(har_file_count):
      hash, _1, offset, size = struct.unpack("<QBII", hix_reader.read(0x11))
      assert _1 == 0
      if os.path.exists(f"{replace_root}/{hash:08x}.png"):
        with open(f"{replace_root}/{hash:08x}.png", "rb") as reader:
          data = reader.read()
        size = len(data)
      else:
        har_reader.seek(offset + 0x0C)
        data = har_reader.read(size)

      offset = har_writer.tell() - 0x0C
      hix_writer.write(struct.pack("<QBII", hash, 0, offset, size))
      har_writer.write(data)


if __name__ == "__main__":
  replace_har(f"{DIR_ORIGINAL_FILES_NSW}/{DIR_HAR}", DIR_HAR_REPLACE, f"{DIR_OUT}/{DIR_HAR}")
