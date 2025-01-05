"""
This script processes image files in a specified directory by reading barcodes from the files,
renaming them based on the detected barcodes, and moving them to an output directory.
It uses the `BarcodeReader` module for barcode detection.

Dependencies:
- `barcode_reader_simple.BarcodeReader`: A module used to read barcodes from image files.
- `shutil` and `os`: Python standard libraries for file operations.

Functions:
- main(): The main entry point of the script.

Workflow:
1. Define paths for the input directory (`PATH`) and output directory (`OUT`).
2. Create the output directory if it does not exist.
3. Gather all `.JPG` files from the input directory.
4. Process each image:
   - Use `BarcodeReader` to detect a barcode in the image.
   - If a barcode is detected:
       - Rename the `.JPG` and its associated `.CR2` file using the barcode as a prefix.
       - Store the mapping of barcodes to new filenames in a dictionary.
   - If no barcode is detected:
       - Use the last detected barcode as a prefix for renaming.
5. Move the renamed files to the output directory.

File Naming and Moving:
- Files are renamed with the barcode as a prefix.
- Associated `.CR2` files are renamed alongside their corresponding `.JPG` files.
- Renamed files are moved to the `OUT` directory.

Notes:
- The script assumes that for each `.JPG` file, a corresponding `.CR2` file exists in the same directory.
- The script processes images sequentially, maintaining order.
"""

from barcode_reader_simple_refactored import BarcodeReader
import shutil
import os
from typing import List, Dict

def main() -> None:
    """
    Main function that processes image files in a specified directory, reads barcodes, renames the files based on the 
    detected barcodes, and moves them to an output directory.

    This function assumes that for each `.JPG` file, there is a corresponding `.CR2` file. It also assumes that 
    the last detected barcode is used when no barcode is found in an image.

    Workflow:
    1. Define paths for the input directory (`PATH`) and output directory (`OUT`).
    2. Create the output directory if it does not exist.
    3. Gather all `.JPG` files from the input directory.
    4. Process each image:
       - Detect a barcode using `BarcodeReader`.
       - Rename the `.JPG` and corresponding `.CR2` files based on the barcode.
       - Store the barcode-to-filename mappings.
    5. Move renamed files to the output directory.
    """
    # Paths for the input directory and output directory
    PATH = r"path_to_images"
    OUT = r"path_to_images\out"

    # Ensure the output directory exists
    if not os.path.exists(OUT):
        os.mkdir(OUT)

    # List to hold the paths of all JPG files in the input directory
    fn_JPG_list: List[str] = [] 
    for fn in os.listdir(PATH):
        if fn.endswith("JPG"):
            fn_JPG_list.append(os.path.join(PATH, fn))

    # Dictionary to map barcodes to file paths and a list to track barcodes
    barcode_dict: Dict[str, str] = {}
    barcode_list: List[str] = []

    # Process each JPG file
    for p in sorted(fn_JPG_list):
        # Read the barcode from the image file
        bcode = BarcodeReader(p)
        if bcode is not None:
            # Clean the barcode value for use in filenames
            clean_barcode = str(bcode).replace("b", "").replace("'", "")
            
            # Generate a new filename using the barcode
            new_fn = os.path.join(PATH, clean_barcode + p.split("\\")[-1])
            print(f"Barcode detected \n\n {p} renamed to \n {new_fn}")

            # Rename both the JPG and corresponding CR2 files
            os.rename(p, new_fn)  # Rename JPG file
            os.rename(p.replace(".JPG", ".CR2"), new_fn.replace(".JPG", ".CR2"))

            # Update the barcode dictionary and list
            barcode_dict[clean_barcode] = new_fn
            barcode_list.append(clean_barcode)
        else:
            # Handle case where no barcode is detected
            print(f"Continuing with barcode {barcode_list[-1]} \n\n {p} renamed to \n {new_fn}")

            # Use the last detected barcode for naming
            new_fn = os.path.join(PATH, barcode_list[-1] + p.split("\\")[-1])
            os.rename(p, new_fn)  # Rename JPG file
            os.rename(p.replace(".JPG", ".CR2"), new_fn.replace(".JPG", ".CR2"))

    # Move processed files to the output directory
    for v in barcode_dict.values():
        src = v.replace(".JPG", ".CR2")
        dst = v.replace(".JPG", ".CR2").replace(PATH, OUT)
        print(f"moving {src} to \n {dst}")

        # Move JPG and CR2 files to the output directory
        shutil.move(v, v.replace(PATH, OUT))
        shutil.move(v.replace("JPG", "CR2"), v.replace("JPG", "CR2").replace(PATH, OUT))

if __name__ == "__main__":
    main()
