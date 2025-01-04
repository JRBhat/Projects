import cv2
import pytesseract
import re
from matplotlib import pyplot as plt
import os
from typing import Dict
import numpy as np

# download and install if necessary ; and assign path to tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"local_path_to_tessaract_install\Tesseract-OCR\tesseract.exe"

#region REGEX tricks and remove hash form fileneame method
# regex for detecting text, numbers and other characters from images

# coord_regx = r"""
# [-+]? # optional sign
# (?:
# (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
# |
#  (?: \d+ \.? ) # 1. 12. 123. etc 1 12 123 etc
# )
#  # followed by optional exponent part if desired
# (?: [Ee] [+-]? \d+ ) ?
# """



# OPTIONAL: cleaning and standardizing vivascope file names
# def rename_file_or_dir(root, dirname):

#     new_dirname = dirname.replace("#", "").replace(" ", "_")
#     os.rename(os.path.join(root, dirname), os.path.join(root, new_dirname))
    
# def chk_dir_for_spaces_and_hashes(root, dirs):

#     for dirname in dirs:
#         if "#" in dirname or " " in dirname:
#             rename_file_or_dir(root, dirname)
    
# def remove_hashes_and_spaces_in_pathdirnames(path):
#     for root, dirs, files in os.walk(path):
#         print(root, dirs, files)
#         if len(dirs) != 0:
#             chk_dir_for_spaces_and_hashes(root, dirs)
#endregion

#1 OCR finding coordinates..................................

def create_img_coord_dict(imagepath: str) -> Dict[str, np.ndarray]:
    """
    Specifies the image slice that corresponds to the text of interest.

    Args:
        imagepath (str): The file path to the image.

    Returns:
        Dict[str, np.ndarray]: A dictionary mapping text labels to their corresponding image slices.
    """
    image = cv2.imread(imagepath)

    text_dict = {
        "filename": image[1000:1000+22, 0:0+180],
        "z": image[1019:1019+25, 0:600]
    }

    return text_dict


def get_text_from_crp_img(crp_img: np.ndarray, testing: bool = False) -> str:
    """
    Retrieves text, symbols, and digits from a cropped image slice using Tesseract OCR.

    Args:
        crp_img (np.ndarray): The cropped image slice.
        testing (bool, optional): If True, returns the thresholded image for testing purposes. Defaults to False.

    Returns:
        str: The extracted text, symbols, and numbers in string format.
    """
    gray_image = cv2.cvtColor(crp_img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding
    threshold_image = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY_INV)[1]

    # Apply OCR
    text = pytesseract.image_to_string(threshold_image)

    if testing:
        return text, threshold_image
    else:
        return text



def extract_text_from_OCR_output(img_path: str, testing: bool = False) -> str:
    """
    Extracts text from an image using OCR and processes the output to retrieve specific information.

    Args:
        img_path (str): The file path to the image.
        testing (bool, optional): If True, displays the thresholded image for testing purposes. Defaults to False.

    Returns:
        str: The extracted filename and z-coordinate.
    """
    filename_regx = r"v[0-9]*.bmp"
    coord_z_regx = r"-?\d+\.\d+ ?um"

    img_coords_dict = create_img_coord_dict(img_path)

    extracted_text_dict = {}
    for k, v in img_coords_dict.items():
        if testing:
            text, thresh_img = get_text_from_crp_img(v, testing)
        else:
            text = get_text_from_crp_img(v)
        extracted_text_dict[k] = str(text)

    filename = re.search(filename_regx, extracted_text_dict["filename"]).group(0)
    z_coord = re.findall(coord_z_regx, extracted_text_dict["z"])[0].replace("um", "").replace(" ", "")

    if testing:
        if z_coord[0] == "-":
            plt.imshow(thresh_img)
            plt.show()
            print(f"neg precedes: {z_coord}")
        elif z_coord[0] == "2" and len(z_coord) > 6:
            plt.imshow(thresh_img)
            plt.show()
            z_coord = z_coord[1:]
            print(f"2 omitted: new {z_coord}")
    else:
        if z_coord[0] == "-":
            print(f"neg precedes: {z_coord}")
        elif z_coord[0] == "2" and len(z_coord) > 6:
            z_coord = z_coord[1:]
            print(f"2 omitted: new {z_coord}")

    return filename, z_coord

def main() -> None:
    """
    Main function to process images in specified directories, extract text using OCR,
    and save the results to output files.
    """
    PATHS = [
        r"Path_to_images_study1",
        r"Path_to_images_study2"
    ]

    for PATH in PATHS:
        OUTPATH = os.path.join(PATH, "out")

        if not os.path.isdir(OUTPATH):
            os.mkdir(OUTPATH)

        for path, _, fn in os.walk(PATH):
            path_parts = path.split("\\")
            if "Block" in path_parts[-1] and "T05" in path_parts[-2]:
                filen, z = extract_text_from_OCR_output(os.path.join(path, fn[0]), testing=False)
                if filen == fn[0]:
                    studyno = PATH.split("\\")[-1]
                    with open(os.path.join(OUTPATH, f"depth_results_{studyno}_LATEST.txt"), "a+") as fd:
                        print(path_parts[-3], path_parts[-2], path_parts[-1], fn[0], z, file=fd)
                    print("1")
                else:
                    print("Filenames do not match")
                    print(fn[0], filen)
                    input("Press enter to continue or ctrl+c to exit...")
                    continue

if __name__ == "__main__":
    main()
