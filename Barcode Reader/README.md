# Barcode Image Processor

This script processes image files in a specified directory, reads barcodes from `.JPG` files, renames them based on the detected barcodes, and moves them to an output directory. It uses the `BarcodeReader` module for barcode detection.

## Dependencies

- `barcode_reader_simple_refactored.BarcodeReader`: A module used to read barcodes from image files.
- Python standard libraries:
  - `shutil`: For file operations.
  - `os`: For file path manipulations.

### Setup

1. Ensure that the necessary Python libraries are installed.
2. Place your image files (in `.JPG` format) and their associated `.CR2` files in a specified input directory.
3. Configure the `PATH` variable to the input directory path, and `OUT` variable to the output directory path in the script.

### Running the Script

1. Clone this repository to your local machine.
2. Navigate to the directory containing the script.
3. Run the script:

   ```bash
   python barcode_processor.py

### How it Works

    Input:
        The script processes .JPG files in the specified input directory.
        It uses the BarcodeReader function to detect barcodes from each image.

    Barcode Detection and Renaming:
        If a barcode is detected, the image and its associated .CR2 file are renamed using the barcode as the prefix.
        If no barcode is detected, the last detected barcode is used as a prefix for renaming.

    File Output:
        The renamed files are moved to a specified output directory.

    File Format:
        The script processes .JPG and .CR2 files, renaming them with the barcode data.

### Notes

    The script assumes that for each .JPG file, a corresponding .CR2 file exists in the same directory.
    The script processes images sequentially and maintains order, using the last detected barcode when no barcode is found in an image.

### Example

Given an image image1.JPG with a detected barcode, the file will be renamed to barcode123_image1.JPG. The associated .CR2 file will also be renamed accordingly.
License

This project is licensed under the MIT License - see the LICENSE file for details.
