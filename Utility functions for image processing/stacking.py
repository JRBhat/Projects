"""
This script processes image files by stacking them vertically and horizontally, adding numbering to filenames, 
and renaming them according to a specified pattern. The images are then saved to a new directory.
"""

import os
import cv2
import numpy as np
from typing import List, Tuple
from Util import check_study_data


def stack_images(subj_path_list: List[str], extn: str, padding_size: int) -> np.ndarray:
    """
    Stacks images from a list into a single image, with padding and numbering for each image.
    
    Args:
    subj_path_list (List[str]): List of paths to the image files to be stacked.
    extn (str): The extension of the images (e.g., ".TIF").
    padding_size (int): The size of the padding to be added between the stacked images.
    
    Returns:
    np.ndarray: The stacked image.
    """
    arr_list = [(cv2.imread(path), path.split("\\")[-1].replace(extn, "")) for path in subj_path_list]

    try:
        stacked_img_left = np.vstack(
            [np.vstack([arr[0], cv2.putText(np.zeros((padding_size, arr[0].shape[1], arr[0].shape[2]), dtype=arr[0].dtype),
                                        str(idx), 
                                        org=(arr[0].shape[1] // 2, padding_size // 2), 
                                        fontFace=cv2.FONT_HERSHEY_DUPLEX, 
                                        fontScale=1.5, 
                                        color=(0, 0, 0),
                                        thickness=4)]) 
             for idx, arr in enumerate(arr_list[:2], start=1)]
        )
        
        stacked_img_right = np.vstack([
            np.vstack([arr[0], cv2.putText(np.zeros((padding_size, arr[0].shape[1], arr[0].shape[2]), dtype=arr[0].dtype),
                                        str(idx), 
                                        org=(arr[0].shape[1] // 2, padding_size // 2), 
                                        fontFace=cv2.FONT_HERSHEY_DUPLEX, 
                                        fontScale=1.5, 
                                        color=(0, 0, 0),
                                        thickness=4)]) 
             for idx, arr in enumerate(arr_list[2:], start=1)
        ])
        
        stacked_img = np.hstack([stacked_img_left, np.zeros((stacked_img_left.shape[0], padding_size, stacked_img_left.shape[2]), dtype=stacked_img_left.dtype), stacked_img_right])
    
    except IndexError:
        raise Exception("Batch contains less than 6 images")

    return stacked_img


def add_numbering_to_fns_in_stack(subj_path_list: List[str], extn: str) -> List[Tuple[str, str]]:
    """
    Adds numbering to the filenames in a list of image file paths.
    
    Args:
    subj_path_list (List[str]): List of image file paths to rename.
    extn (str): The extension of the images (e.g., ".TIF").
    
    Returns:
    List[Tuple[str, str]]: List of tuples containing old and new filenames.
    """
    path_tup_list = [(path, os.path.join("\\".join(path.split("\\")[:-1]), path.split("\\")[-1].replace(extn, f"_{idx}{extn}"))) 
                     for idx, path in enumerate(subj_path_list, start=1)]
    
    return path_tup_list


def rename_files(rename_list: List[Tuple[str, str]], basepath: str) -> None:
    """
    Renames files based on the provided list of old and new filenames.
    
    Args:
    rename_list (List[Tuple[str, str]]): List of tuples containing old and new filenames.
    basepath (str): The base directory where the files are located.
    """
    for path_tuple in rename_list:
        os.rename(path_tuple[0], path_tuple[1])
        os.rename(path_tuple[0].replace(".TIF", ".jpg"), path_tuple[1].replace(".TIF", ".jpg"))
        
        old = path_tuple[0].split("\\")[-1]
        new = path_tuple[1].split("\\")[-1]
        
        print(f"{old} -----> {new}")
        
        with open(os.path.join(basepath, "conversion_map.txt"), "a+") as conv_f:
            print(f"{old} -----> {new}", file=conv_f)


def main() -> None:
    """
    Main function to process the image files: stack them, add numbering, and rename them.
    """
    BASEPATH = r"path_to_images"
    OUTDIR = os.path.join(BASEPATH, "stacked_without_fns")
    EXTN = ".TIF"
    PAD_SIZE = 100
    
    if not os.path.exists(OUTDIR):
        os.mkdir(OUTDIR)
        
    InputFileParseMask = "S(?P<subj_int>[0-9]*)F(?P<side_int>[0-9]{2})T(?P<time_int>[0-9]{2})", 
    InputFileParameters = [
        "subj_int",
        "side_int", 
        "time_int"
    ]
    
    study_data = check_study_data(BASEPATH, f"*{EXTN}", InputFileParseMask, InputFileParameters, 1, search_depth=0, key_remove_list=[])
    
    subj_id_list = sorted(set([st[0] for st in study_data]))
    time_id_list = sorted(set([st[2] for st in study_data]))
    
    for id in [2, 3]:
        for t in [3]:
            subj_group = [d[-1] for d in study_data if id == d[0] and t == d[2]]
            if subj_group:
                fn = subj_group[0].split("\\")[-1].split("_")[0] + f"_stacked{EXTN}"
                stacked_img = stack_images(subj_group, EXTN, PAD_SIZE)
                
                if isinstance(stacked_img, np.ndarray):
                    cv2.imwrite(os.path.join(OUTDIR, fn), stacked_img)
                    print(fn)
                else:
                    print(f"{fn} missing...will be skipped")
                    continue
            else:
                fn = [f"S0{id}", f"S0{id}"][len(str(id)) > 2] + f"F01T0{t}ABC9999{EXTN}"
                print(f"{fn} missing stack")
                continue


if __name__ == "__main__":
    main()
