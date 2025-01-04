 # Confocal Microscopic Image Processing and Analysis

This repository contains a collection of Python scripts for processing and analyzing confocal microscopic images. The scripts perform various tasks such as image resizing, OCR text extraction, file renaming, and creating image overlays.

## Installation

To use these scripts, you need to have Python installed along with the following dependencies:

- `opencv-python`
- `pytesseract`
- `matplotlib`
- `numpy`
- `shutil`
- `os`
- `re`
- `pickle`
- `time`

You can install the required dependencies using pip:

## shell
pip install opencv-python pytesseract matplotlib numpy shutil

Additionally, ensure that Tesseract OCR is installed and the path to the Tesseract executable is correctly set in the scripts.
Usage

Each script can be run independently. Make sure to update the file paths and other parameters as needed before running the scripts.


## Scripts

**Image Resizing and Concatenation**

    Script: image_resizing_concatenation.py
    Description: Resizes images to specified dimensions and concatenates them horizontally or vertically.
    Functions:
        resize_img: Resizes an image to the specified dimensions.
        transform_imgs_into_standard_dimensions: Resizes multiple images to standard dimensions and returns them as a tuple.
        main: Main function to resize and concatenate images.

**OCR Text Extraction**

    Script: ocr_text_extraction.py
    Description: Extracts text from images using OCR and processes the output to retrieve specific information.
    Functions:
        create_img_coord_dict: Specifies the image slice that corresponds to the text of interest.
        get_text_from_crp_img: Retrieves text, symbols, and digits from a cropped image slice using Tesseract OCR.
        extract_text_from_img_coords: Extracts text from an image using OCR and processes the output.
        main: Main function to process images and extract text using OCR.

**File Renaming**

    Script: file_renaming.py
    Description: Renames files in a specified directory based on certain conditions.
    Functions:
        rename_files_in_directory: Renames files in the specified directory based on the presence of specific substrings in their filenames.
        main: Main function to rename files in the specified directory.

**Image Overlay Creation**

    Script: image_overlay_creation.py
    Description: Creates an overlay image using thresholding and binary inversion.
    Functions:
        resize_img: Resizes an image to the specified percentage of its original size.
        create_overlay_using_thresh_bin_inv: Creates an overlay image using thresholding and binary inversion.

**Macroscopic Image Copying**

    Script: macroscopic_image_copying.py
    Description: Copies macroscopic images from the specified base directory to the output directory.
    Functions:
        copy_macroscopic_images: Copies macroscopic images from the base directory to the output directory.
        main: Main function to copy macroscopic images.

**Coordinate Extraction**

    Script: coordinate_extraction.py
    Description: Extracts text coordinates from images in the specified directory using OCR.
    Functions:
        main: Main function to extract text coordinates from images in the specified directory.

**Contributing**

Contributions are welcome! Please open an issue or submit a pull request.

**License**

This project is licensed under the MIT License. See the LICENSE file for details