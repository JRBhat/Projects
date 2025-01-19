from PIL import Image
import os
import shutil
import sys
import numpy as np
import pickle
from collections import defaultdict
from typing import Dict, List, Tuple

# Constants
PATH_BEFORE_CONV = r"path_to_original_jpgs\orig_jpgs"
PATH_CONV_CLEANED = r"path_to_conv_images_after_postprocessing_using_canon_software\jpgs_conv_cleaned"
PATH_AFTER_CONV = r"path_after_conv\conv_jpgs"
PATH_ORPHAN_IMG = r"path_to_picked_jpgs\orphan_jpg"
PATH_MAIN = ("\\").join(PATH_ORPHAN_IMG.split("\\")[:-1])
LOG_FILENAME = os.path.join(PATH_MAIN, "transformation.log")
PATH_OUTPUT = r"path_to_output\out"

def main() -> None:
    """
    Main function to prepare directories, create transformation dictionary, and find orphaned images.
    """
    if not os.path.exists(PATH_OUTPUT):
        os.mkdir(PATH_OUTPUT)

    prepare_training_jpg_dirs(PATH_BEFORE_CONV, PATH_CONV_CLEANED, PATH_AFTER_CONV, LOG_FILENAME)
    transformation_dict = create_transformation_dict(PATH_MAIN, PATH_BEFORE_CONV, PATH_AFTER_CONV, LOG_FILENAME)
    find_orphaned_jpg(transformation_dict, PATH_OUTPUT, PATH_ORPHAN_IMG, LOG_FILENAME)

def prepare_training_jpg_dirs(
    path_before_conversion: str, path_conv_cleaned: str, path_after_conversion: str, log_file: str
) -> None:
    """
    Prepare directories for training JPGs by copying relevant files.

    :param path_before_conversion: Path to original JPGs before conversion.
    :param path_conv_cleaned: Path to cleaned converted JPGs.
    :param path_after_conversion: Path to store JPGs after conversion.
    :param log_file: Path to log file for errors and status.
    """
    jpg_name_dict = {fn: "" for fn in os.listdir(path_before_conversion)}

    ext = ""
    for fn in os.listdir(path_conv_cleaned):
        if ext == "":
            ext = os.path.splitext(fn)
        if fn in jpg_name_dict.keys():
            jpg_name_dict[fn] = os.path.join(path_conv_cleaned, fn)

    error = 0
    for k, v in jpg_name_dict.items():
        try:
            new_path_name = os.path.join(path_after_conversion, k)
            shutil.copyfile(v, new_path_name)
        except Exception as Argument:
            with open(log_file, "a+") as fl:
                fl.write(str(Argument))
                fl.write(f"Missing in conv cleaned: no value found for {k}\n")
                fl.write("ERROR\n")
                error = 1

    if len(os.listdir(path_before_conversion)) == len(os.listdir(path_after_conversion)):
        with open(log_file, "a+") as fl:
            fl.write("LENGTHS ARE EQUAL - CHECK OK\n")
    else:
        with open(log_file, "a+") as fl:
            fl.write("Lengths of folders before and after processing are not equal. Please check folders.\n")
            fl.write("ERROR\n")
            error = 1

    if error == 0:
        print(jpg_name_dict)
        with open(log_file, "a+") as fl:
            print("Copied files are as follows:", file=fl)
            print(jpg_name_dict, file=fl)
            print("COPY OK")
    else:
        print("Exiting... Errors found. See log file.")
        sys.exit(1)

def create_transformation_dict(
    main_path: str, path_before_conversion: str, path_after_conversion: str, log_file: str
) -> Dict[Tuple[int, int, int], List[int]]:
    """
    Create a transformation dictionary mapping RGB values from original to converted images.

    :param main_path: Main directory path.
    :param path_before_conversion: Path to original JPGs before conversion.
    :param path_after_conversion: Path to converted JPGs.
    :param log_file: Path to log file for errors and status.
    :return: Transformation dictionary.
    """
    transformation_dict: Dict[Tuple[int, int, int], List[int]] = {}

    if os.path.exists(os.path.join(main_path, "transformation_dict.pickle")):
        with open(os.path.join(main_path, "transformation_dict.pickle"), 'rb') as saved_file:
            try:
                transformation_dict = pickle.load(saved_file)
            except Exception:
                pass

    if not transformation_dict:
        print("No saved pickle found. Creating one again. Takes a while so go grab a coffee.")
        for fn in os.listdir(path_before_conversion):
            try:
                img_orig = Image.open(os.path.join(path_before_conversion, fn))
                img_conv = Image.open(os.path.join(path_after_conversion, fn))

                width, height = img_orig.size

                block_array = np.dstack([np.array(img_orig), np.array(img_conv)])
                block_array_reshaped = block_array.reshape(height * width, 6)

                list_ll = [[tuple(a[:3]), tuple(a[3:])] for a in block_array_reshaped]
                temp_dict = defaultdict(list)
                for key, val in list_ll:
                    temp_dict[key].append(val)

                image_dict = {
                    key: np.median(np.array(val), axis=0).astype(int).tolist()
                    for key, val in temp_dict.items()
                }

            except Exception as Argument:
                with open(log_file, "a+") as fl:
                    fl.write(str(Argument))
                    fl.write("Exceptions found\n")

            transformation_dict.update(image_dict)
            print(f"Finished merging dict of {fn}")

        with open(os.path.join(main_path, "transformation_dict.pickle"), 'wb') as saved_file:
            pickle.dump(transformation_dict, saved_file)

    else:
        input("Pre-existing pickled file found. Proceed to use it? Press Enter to continue...")

    return transformation_dict

def find_orphaned_jpg(
    transformation_dict: Dict[Tuple[int, int, int], List[int]], outpath: str, path_orphan_image: str, log_file: str
) -> None:
    """
    Apply transformation to orphaned JPGs and save results.

    :param transformation_dict: Dictionary mapping original to transformed RGB values.
    :param outpath: Output directory for transformed orphaned images.
    :param path_orphan_image: Path to orphaned images.
    :param log_file: Path to log file for errors and status.
    """
    for fn in os.listdir(path_orphan_image):
        img_orphan = Image.open(os.path.join(path_orphan_image, fn))
        img_orphan_cp = img_orphan.copy()

        width, height = img_orphan_cp.size
        dummy_array = np.array(img_orphan.copy())

        for y in range(height):
            for x in range(width):
                RGB_orphan = img_orphan.getpixel((x, y))

                try:
                    dummy_array[y, x, :] = np.array(transformation_dict[RGB_orphan])
                except KeyError:
                    with open(log_file, "a+") as fl:
                        fl.write(f"Key not found for {RGB_orphan}. Replacing with nearest match.\n")
                    dummy_array[y, x, :] = np.array(find_closest_RGB_neighbour(RGB_orphan, transformation_dict))

        new_fn = fn.replace(".jpg", "_conv.jpg")
        img_orphan_cp1 = Image.fromarray(dummy_array)
        img_orphan_cp1.save(os.path.join(outpath, new_fn))

def find_closest_RGB_neighbour(
    RGB_tuple: Tuple[int, int, int], transf_dict: Dict[Tuple[int, int, int], List[int]]
) -> List[int]:
    """
    Find the closest RGB neighbor in the transformation dictionary.

    :param RGB_tuple: RGB tuple of the orphaned pixel.
    :param transf_dict: Transformation dictionary.
    :return: Closest RGB neighbor.
    """
    ro, go, bo = RGB_tuple
    x = 1

    while True:
        for n in [1, -1]:
            r, g, b = ro + x * n, go + x * n, bo + x * n
            r, g, b = map(check_if_valid_RGB_value, (r, g, b))

            if transf_dict.get((r, go, bo)):
                return transf_dict[(r, go, bo)]
            if transf_dict.get((ro, g, bo)):
                return transf_dict[(ro, g, bo)]
            if transf_dict.get((ro, go, b)):
                return transf_dict[(ro, go, b)]
        x += 1

def check_if_valid_RGB_value(number: int) -> int:
    """
    Ensure the RGB value is within the valid range (0-255).

    :param number: RGB value.
    :return: Corrected RGB value.
    """
    return max(0, min(255, number))

if __name__ == "__main__":
    main()
