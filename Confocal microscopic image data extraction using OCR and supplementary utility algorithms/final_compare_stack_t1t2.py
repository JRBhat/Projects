
import os
import re
import cv2
from typing import Union, Tuple
import numpy as np

def concat_custom(*args: str) -> Union[np.ndarray, None]:
    """
    Concatenates images either vertically or horizontally based on the number of input images.

    Args:
        *args (str): Variable length argument list of image file paths to be concatenated.

    Returns:
        Union[np.ndarray, None]: The concatenated image if successful, otherwise None.
    """
    if len(args) == 3:
        for n, path in enumerate(args):
            if n == 0:
                img = cv2.imread(path)
                continue
            img2 = cv2.imread(path)
            hstackimg = cv2.vconcat([img, img2])
            if n == len(args) - 1:
                return hstackimg
            img = hstackimg

    if len(args) == 2:
        for n, img in enumerate(args):
            if n == 0:
                img1 = img
                continue
            vstackimg = cv2.hconcat([img1, img])
        return vstackimg.astype("uint8")
    
def main():

    PATHS = [
        r"microscopic_images_path\piased_t1\block_imgs_out\jpgs",
        r"microscopic_images_path\piased_t1\macros_out\jpgs",
        r"microscopic_images_path\piased_t1\macros_out\out_overlayed_latest",
        r"microscopic_images_path\piased_t57\block_imgs_out\jpgs",
        r"microscopic_images_path\piased_t57\macros_out\jpgs",
        r"microscopic_images_path\piased_t57\macros_out\out_overlayed_latest"
    ]

    REGSUB = r"S[0-9]{2}"
    REGTIME = r"T[0-9]{1}"

    OUTPATHT1 = r"microscopic_images_path\final_vstack_t1"
    OUTPATHT2 = r"microscopic_images_path\final_vstack_t2"

    if not os.path.isdir(OUTPATHT1):
        os.mkdir(OUTPATHT1)

    if not os.path.isdir(OUTPATHT2):
        os.mkdir(OUTPATHT2)

    subj_list = []
    time_list = []

    for PATH in PATHS:
        for fn in os.listdir(PATH):
            if re.search(REGSUB, fn) and re.search(REGTIME, fn):
                subj_list.append(re.search(REGSUB, fn).group(0))
                time_list.append(re.search(REGTIME, fn).group(0))

    subj_list = sorted(set(subj_list))
    time_list = sorted(set(time_list))

    block_dict = {
        (s, t): os.path.join(PATH, fn)
        for s in subj_list
        for t in time_list
        for PATH in PATHS
        for fn in os.listdir(PATH)
        if s in fn and t in fn and "VivaBlock1" in fn and not "macro" in fn and fn.endswith(".jpg")
    }
    macro_dict = {
        (s, t): os.path.join(PATH, fn)
        for s in subj_list
        for t in time_list
        for PATH in PATHS
        for fn in os.listdir(PATH)
        if s in fn and t in fn and "v0000000" in fn and fn.endswith(".jpg")
    }
    overlay_dict = {
        (s, t): os.path.join(PATH, fn)
        for s in subj_list
        for t in time_list
        for PATH in PATHS
        for fn in os.listdir(PATH)
        if s in fn and t in fn and "thresh" in fn and fn.endswith(".jpg")
    }

    print(block_dict, macro_dict, overlay_dict)

    for s in subj_list:
        hstackt1 = concat_custom(block_dict[(s, list(time_list)[0])], macro_dict[(s, list(time_list)[0])], overlay_dict[(s, list(time_list)[0])])
        hstackt2 = concat_custom(block_dict[(s, list(time_list)[1])], macro_dict[(s, list(time_list)[1])], overlay_dict[(s, list(time_list)[1])])
        cv2.imwrite(os.path.join(OUTPATHT1, f"{s}_concatenated_stackt1.jpg"), hstackt1)
        cv2.imwrite(os.path.join(OUTPATHT2, f"{s}_concatenated_stackt2.jpg"), hstackt2)

if __name__ == "__main__":
    main()