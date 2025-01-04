import cv2
import pytesseract
import re
from matplotlib import pyplot as plt
import os
import sys
import numpy as np
from Util import readData, writeData
from vivascope_files_cleaning_util import remove_hashes_and_spaces_in_pathdirnames
from typing import Dict, Tuple


pytesseract.pytesseract.tesseract_cmd = r"local_path_to_tessaract_install\Tesseract-OCR\tesseract.exe"

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




def create_img_coord_dict(imagepath: str) -> Tuple[Dict[str, np.ndarray], np.ndarray]:
    """
    Specifies the image slice that corresponds to the text of interest.

    Args:
        imagepath (str): The file path to the image.

    Returns:
        Tuple[Dict[str, np.ndarray], np.ndarray]: A dictionary mapping text labels to their corresponding image slices and the original image.
    """
    image = cv2.imread(imagepath)

    text_dict = {
        "filename": image[1000:1000+22, 0:0+180],
        "x": image[1019:1019+25, 0:600],
        "y": image[1019:1019+25, 0:600]
    }

    return text_dict, image

def get_text_from_crp_img(crp_img: np.ndarray) -> str:
    """
    Retrieves text, symbols, and digits from a cropped image slice using Tesseract OCR.

    Args:
        crp_img (np.ndarray): The cropped image slice.

    Returns:
        str: The extracted text, symbols, and numbers in string format.
    """
    gray_image = cv2.cvtColor(crp_img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding
    threshold_image = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY_INV)[1]

    plt.imshow(threshold_image)

    # Apply OCR
    text = pytesseract.image_to_string(gray_image)

    return text


def extract_text_from_img_coords(img_path: str) -> Tuple[str, str, str]:
    """
    Extracts text from an image using OCR and processes the output to retrieve specific information.

    Args:
        img_path (str): The file path to the image.

    Returns:
        Tuple[str, str, str]: The extracted filename, x-coordinate, and y-coordinate.
    """
    filename_regx = r"v[0-9]*.bmp"

    img_coords_dict, img = create_img_coord_dict(img_path)

    extracted_text_dict = {}
    for k, v in img_coords_dict.items():
        text = get_text_from_crp_img(v)
        extracted_text_dict[k] = str(text)

    print(extracted_text_dict)

    filename = re.search(filename_regx, extracted_text_dict["filename"]).group(0)
    x_coord = re.findall(r'[-+]?\d*\.\d+', extracted_text_dict["x"])[0]
    imgx = np.array(img[1029:1029+3, 21:21+1])

    # Count the number of black pixels in the image
    num_black_pixels_x = np.count_nonzero(imgx == 0)

    if x_coord[0] != "-" and num_black_pixels_x == 3:
        x_coord = "-" + x_coord

    y_coord = re.findall(r'[-+]?\d*\.\d+', extracted_text_dict["y"])[1]
    imgy = np.array(img[1029:1029+3, 105:105+1])

    # Count the number of black pixels in the image
    num_black_pixels_y = np.count_nonzero(imgy == 0)

    if y_coord[0] != "-" and num_black_pixels_y == 3:
        y_coord = "-" + y_coord

    print(num_black_pixels_x, num_black_pixels_y)
    print(filename, x_coord, y_coord)

    return filename, x_coord, y_coord
def main() -> None:
    """
    Main function to process images in the specified directory, extract coordinates,
    and save the results to a dictionary.
    """
    PATH = r"path_to_images"
    # remove_hashes_and_spaces_in_pathdirnames(PATH)

    subj_dict = {}
    for root, dirs, _ in os.walk(PATH):
        if len(dirs) != 0:
            subj_no = None
            Block_dict = {}
            Stack_dict = {}
            for dirname in dirs:
                if "VivaBlock" in dirname:
                    subj_no = re.search(r"S[0-9]{2}", root).group(0)
                    folderpath = os.path.join(root, dirname)
                    img_tup_list_temp = []
                    for imgname in os.listdir(folderpath):
                        if imgname[0] == "v" and "#" not in imgname:
                            fn, x, y = extract_text_from_img_coords(os.path.join(folderpath, imgname))
                            img_tup_list_temp.append((x, y, os.path.join(folderpath, fn)))
                    Block_dict[dirname] = img_tup_list_temp

                elif "VivaStack" in dirname:
                    subj_no = re.search(r"S[0-9]{2}", root).group(0)
                    folderpath = os.path.join(root, dirname)
                    for imgname in os.listdir(folderpath):
                        if imgname == "v0000000.bmp":
                            fn, x, y = extract_text_from_img_coords(os.path.join(os.path.join(root, dirname), imgname))
                            Stack_dict[dirname] = (x, y, os.path.join(folderpath, fn))

            if subj_no is not None and "S" in subj_no:
                subj_dict[subj_no] = [Stack_dict, Block_dict]

    print(subj_dict)
    writeData(subj_dict, r"path\data\data_dict")

if __name__ == "__main__":
    main()
