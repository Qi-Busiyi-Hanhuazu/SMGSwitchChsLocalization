# Clean output folder
if (Test-Path -Path "out\" -PathType "Container") {
  Remove-Item -Recurse -Force "out\"
}
if (Test-Path -Path "temp\" -PathType "Container") {
  Remove-Item -Recurse -Force "temp\"
}

python scripts\extract_har.py
python scripts\extract_arc.py
python scripts\convert_bmg_from_texts.py
python scripts\create_font.py
python scripts\import_arc.py

New-Item -Path "temp\texture_replace" -ItemType Directory -Force | Out-Null
Copy-Item -Path "files\images\*.png" -Destination "temp\texture_replace" -Force

python scripts\replace_har.py

Copy-Item -Path "files\romfs\data\" -Destination "out\010049900f546003\romfs\" -Recurse -Force
New-Item -Path "out\010049900f546003\v1.0.0.txt" -ItemType "File" -Force | Out-Null

Compress-Archive -Path "out\010049900f546003\" -Destination "out\patch-switch.zip" -Force
