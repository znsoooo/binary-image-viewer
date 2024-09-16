# Binary Image Viewer

Binary Image Viewer is a desktop application built with wxPython, designed to view and convert binary image files. It supports a variety of image formats, and provides to load, display, and save images with different settings.

The binary image files format arranged in a row-major order, supporting 1-channel (gray), 3-channel (RGB), and 4-channel (RGBA) images.

It also supports reading other formats of image files, provide channels conversion and file saving.


## Features

- Load and display binary files as images.
- Set the width, height, and channels for showing binary image data.
- Support for other normal image formats.
- Ability to save displayed images back to binary or image files.
- Navigate through images in a directory using keyboard shortcuts.


## Usage

- **Open a File**: Use `Ctrl + O` to open a binary or image file, or simply drag and drop the file onto the application window.
- **Save a File**: Use `Ctrl + S` to save the currently viewed image to a BIN or PNG file. PNG is a lossless compression format.
- **Navigate**: Use `PgUp` / `PgDn` to navigate through images in the current directory.
- **Exit**: Press `Esc` to exit the application.


## Settings

- **Width**: Set the width of the binary image.
- **Height**: Set the height of the binary image.
- **Channels**: Set the number of channels (1 for GRAY, 3 for RGB, and 4 for RGBA).
- **Path**: Set the file path to open a binary or a normal image file.


## License

- __Author:__ Shixian Li
- __QQ:__ 11313213
- __Email:__ <lsx7@sina.com>
- __GitHub:__ <https://github.com/znsoooo/binary-image-viewer>
- __License:__ MIT License. Copyright (c) 2024 Shixian Li (znsoooo). All Rights Reserved.


## Notice!!

The Binary Image Viewer is NOT a full-featured image viewer, it is designed for reading binary image files, so it is NOT planed to support comprehensive image editing, such as scaling, cropping, marking, or others complex features.
