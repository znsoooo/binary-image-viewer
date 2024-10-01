@echo off
python -m PyInstaller -yw BinImgViewer.py --icon icon.ico --add-data=icon.ico;. --version-file file_version_info.txt
pause
