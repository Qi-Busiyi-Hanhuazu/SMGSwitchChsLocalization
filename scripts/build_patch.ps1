# Clean output folder
if (Test-Path -Path "out\" -PathType "Container") {
  Remove-Item -Recurse -Force "out\"
}
if (Test-Path -Path "temp\" -PathType "Container") {
  Remove-Item -Recurse -Force "temp\"
}

python scripts\extract_files_from_arc.py
python scripts\convert_bmg_from_texts.py
python scripts\copy_font.py
python scripts\import_files_into_arc.py

Compress-Archive -Path "out/010049900f546003/" -Destination "out/patch-switch.zip" -Force
