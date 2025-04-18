import os

from rarc import Rarc
from yaz0 import Yaz0

FILE_LIST = {
  "nsw": (
    "LayoutData/Font.arc",
    "MessageData/Message.arc",
  ),
  "wii": (
    "Font.arc",
    "Message.arc",
  ),
  "wii_cn": (
    "Font.arc",
    "Message.arc",
  ),
}

for folder, file_list in FILE_LIST.items():
  for file_path in file_list:
    with open(f"original_files/{folder}/{file_path}", "rb") as reader:
      data = reader.read()

    if data[:4] == b"Yaz0":
      data = Yaz0.decompress(data, ">")
    rarc = Rarc(data)

    output_dir = f"unpacked/{folder}/{os.path.basename(file_path).rsplit('.', 1)[0]}"
    os.makedirs(output_dir, exist_ok=True)
    for file_name in rarc.files:
      with open(f"{output_dir}/{file_name.name}", "wb") as writer:
        writer.write(file_name.data)
