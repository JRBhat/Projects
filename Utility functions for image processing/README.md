# Image Processing Module for Stacking, Renaming, Metadata analysis and Organizing Images

This Python module is designed to process images for research purposes. It provides functionalities to stack images vertically and horizontally, add numbering to filenames, and rename files according to a specified pattern. This module is useful for organizing and preparing images for further analysis or archival purposes.

## Features

- **Image Stacking**: Stack images vertically and horizontally with padding between them. The images are stacked in groups of two on the left and right side of the final image.
- **Filename Numbering**: Adds numbering to the filenames of images, enabling sequential tracking.
- **File Renaming**: Renames files based on a pattern derived from study metadata (e.g., subject ID, timepoint, etc.).
- **Error Handling**: Ensures that the correct number of images are available for stacking, and provides feedback if files are missing or errors occur.
- **Calculates Time Delta**: Plots the differences in the timepoints on a graph to analyse any discrepencies(if any) during the photo acquisition.

## Installation

Ensure you have the following Python dependencies installed:

- `opencv-python` for image processing
- `numpy` for numerical operations
- `exifread` for image exif metadata extraction

You can install these dependencies using `pip`:

```bash
pip install opencv-python numpy exifread
