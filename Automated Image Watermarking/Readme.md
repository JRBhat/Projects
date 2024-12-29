# Image Watermarking Utility

This project contains scripts and tools to watermark images using different methods: recursive directory processing, Python's PIL library, and batch scripting with ImageMagick. The watermarking process supports various image formats including JPG, PNG, and TIFF.

## Modules

### 1. Python Watermarking (`watermark_images.py`)

This script walks through a directory and applies watermarks to images using Python's `PIL` library. It offers two types of watermarking:

- **Center Position**: Watermarks the image in the center.
- **Corner Position**: Watermarks the image in the bottom-right corner.

#### Usage:
- Modify the `img_inp_path` variable to point to the folder containing images.
- The watermark image is specified by its path.
- Transparency (`alpha`) is adjustable (from 0 to 1).

### 2. Recursive Directory Watermarking (`directory_watermark.py`)

This script iterates recursively through directories, renaming files with appropriate extensions, and applying watermarks using a batch script.

#### Features:
- Renames image files to standard formats (e.g., `.jpg`, `.png`).
- Applies watermarking in subdirectories while avoiding previously processed directories.

### 3. Batch Watermarking (`watermark_batch.bat`)

A batch script for watermarking images using **ImageMagick**. It processes all images in the specified directory and applies a watermark in either the bottom-right or top-left corner. It also manages directories for input and output, creating the necessary structure for organized watermarking.

#### Requirements:
- ImageMagick must be installed and available in the system's PATH.
  
## Installation

1. Install dependencies for Python:
   ```bash
   pip install pillow
