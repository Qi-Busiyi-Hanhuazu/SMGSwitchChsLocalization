import os

from rarc import Rarc
from yaz0 import Yaz0

FILE_LIST = {
  "nsw": (
    "LayoutData/Font.arc",
    "MessageData/Message.arc",
  ),
}

folder = "nsw"
file_list = FILE_LIST["nsw"]
for file_path in file_list:
  with open(f"original_files/{folder}/{file_path}", "rb") as reader:
    data = reader.read()

  if data[:4] == b"Yaz0":
    data = Yaz0.decompress(data, ">")
    output_dir = f"unpacked/{folder}/{os.path.basename(file_path)}"
    os.makedirs(os.path.dirname(output_dir), exist_ok=True)
    with open(output_dir, "wb") as writer:
      writer.write(data)
  rarc = Rarc(data)

  for file in rarc.files:
    replace_path = f"temp/import/{os.path.basename(file_path).rsplit('.', 1)[0]}/{file.name}"
    if not os.path.exists(replace_path):
      continue
    with open(replace_path, "rb") as reader:
      file.data = reader.read()

  output_dir = f"out/010049900f546003/romfs/JpJapanese/{file_path}"
  os.makedirs(os.path.dirname(output_dir), exist_ok=True)
  with open(output_dir, "wb") as writer:
    writer.write(rarc.save())
