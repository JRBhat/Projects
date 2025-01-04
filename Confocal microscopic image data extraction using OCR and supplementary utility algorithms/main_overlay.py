
import os
import pathlib
import re
from typing import List

from thresh_otsu_binary_main import create_overlay_using_thresh_bin_inv



def create_regx_list(regx_pattern: str, path: str) -> List[str]:
    """
    Creates a sorted list of unique barcodes extracted from filenames in the specified directory using a regex pattern.

    Args:
        regx_pattern (str): The regex pattern to extract barcodes from filenames.
        path (str): The directory path containing the files.

    Returns:
        List[str]: A sorted list of unique barcodes.
    """
    regx_list = []
    for fn in os.listdir(path):
        barcode = re.search(regx_pattern, fn).group(0)
        regx_list.append(barcode)
    return sorted(set(regx_list))


def set_forground_background_as_per_subjectno(regx_list: List[str], path: str) -> dict:
    """
    Creates a dictionary mapping barcodes to their corresponding foreground and background images.

    Args:
        regx_list (List[str]): A list of barcodes.
        path (str): The directory path containing the files.

    Returns:
        dict: A dictionary mapping barcodes to lists of foreground and background image filenames.
    """
    foreg_backg_dict = {}

    for barcode in regx_list:
        temp_ls = []
        for fn in os.listdir(path):
            if barcode in fn and "block" in fn:
                temp_ls.insert(0, fn)
            elif barcode in fn and "block" not in fn:
                temp_ls.append(fn)
        if len(temp_ls) == 2:
            print(temp_ls)
            foreg_backg_dict[barcode] = temp_ls

    print(foreg_backg_dict)
    return foreg_backg_dict

def main() -> None:
    """
    Main function to process images in specified directories, create overlayed images, and save them to output directories.
    """
    REGX = r"S[0-9]{2}"
    PATHS = [
        r"path\piased_t57\macros_out\jpgs",
        r"path\Vivascope\piased_t1\macros_out\jpgs"
    ]

    for PATH in PATHS:
        PATH_OUT = os.path.join("\\".join(PATH.split("\\")[:-1]), "out_overlayed_latest")

        if not os.path.isdir(PATH_OUT):
            os.mkdir(PATH_OUT)

        Regx_list = create_regx_list(REGX, PATH)
        Forgnd_Backgnd_dict = set_forground_background_as_per_subjectno(Regx_list, PATH)

        for k, v in Forgnd_Backgnd_dict.items():
            create_overlay_using_thresh_bin_inv(v[0], v[1], PATH, PATH_OUT, k, 255, 100)

if __name__ == "__main__":
    main()
