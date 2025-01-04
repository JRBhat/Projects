

import cv2
import numpy as np
import os
from typing import Tuple

# # Load the images
# gray_image_with_rectangle = cv2.imread(r"D:\Code\Software_test_sample_data\viva_mapping\S03F1T1R01_001_macroscopic_image_S03F1T1R01_001_block_3.jpg")
# replacement_image = cv2.imread(r"D:\Code\Software_test_sample_data\viva_mapping\S03F1T1R01_001_macroscopic_image.jpg")



def resize_img(perc: float, img: np.ndarray) -> np.ndarray:
    """
    Resizes an image to the specified percentage of its original size.

    Args:
        perc (float): The percentage to which the image should be resized.
        img (np.ndarray): The input image to be resized.

    Returns:
        np.ndarray: The resized image.
    """
    height, width = img.shape[:2]
    perc = perc / 100
    new_size = (int(round(height * perc, 0)), int(round(width * perc, 0)))
    res_img = cv2.resize(img, new_size)
    return res_img

def create_overlay_using_thresh_bin_inv(foreground_imname: str, background_imname: str, path: str, outpath: str, subjno: str, minIntensity: int, maxIntensity: int) -> None:
    """
    Creates an overlay image using thresholding and binary inversion.

    Args:
        foreground_imname (str): The filename of the foreground image.
        background_imname (str): The filename of the background image.
        path (str): The directory path containing the images.
        outpath (str): The output directory path where the result will be saved.
        subjno (str): The subject number to be included in the output filename.
        minIntensity (int): The minimum intensity value for thresholding.
        maxIntensity (int): The maximum intensity value for thresholding.
    """
    foreground = cv2.imread(os.path.join(path, foreground_imname))
    background = cv2.imread(os.path.join(path, background_imname))

    if not foreground.size == background.size:
        foreground = resize_img(50, foreground)
        background = resize_img(50, background)

    gray = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, minIntensity, maxIntensity, cv2.THRESH_BINARY_INV)
    mask_inv = cv2.bitwise_not(mask)

    result1 = cv2.bitwise_and(foreground, foreground, mask=mask)
    result2 = cv2.bitwise_and(background, background, mask=mask_inv)
    add_result = cv2.add(result1, result2)

    time_no = ""
    if "t1" in outpath:
        time_no = "F1_T1"
    elif "t57" in outpath:
        time_no = "F1_T2"

    cv2.imwrite(os.path.join(outpath, f'{subjno}_{time_no}_thresh_binaryInv_{minIntensity}-{maxIntensity}.jpg'), add_result)
