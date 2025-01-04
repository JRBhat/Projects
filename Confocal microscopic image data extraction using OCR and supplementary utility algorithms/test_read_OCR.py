from MAIN__read_text_from_img_using_OCR import extract_text_from_img_coords
import os
from typing import Tuple

def main() -> None:
    """
    Main function to extract text coordinates from images in the specified directory.

    The function iterates through the files in the specified directory,
    extracts text coordinates from each image using OCR, and prints the results.
    """
    path = r"path\read_text_OCR\path\S03\F1_T1\VivaBlock_1"

    for fn in os.listdir(path):
        coord_tup = extract_text_from_img_coords(os.path.join(path, fn))
        print(coord_tup)

if __name__ == "__main__":
    main()
