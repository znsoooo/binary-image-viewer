@echo off
pyinstaller -yw BinImgViewer.py --icon icon.ico --add-data=icon.ico;.
pause
