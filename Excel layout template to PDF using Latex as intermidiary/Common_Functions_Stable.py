"""
This module contains various utility functions for improving clarity, consistency, and debugging 
while reducing code redundancy and potential errors caused by complex, interdependent code.
"""

import subprocess
import os
import re
from string import digits
import shutil
import datetime
import glob
from ImageAnalysis import Util
import cv2
import sys
from typing import List, Dict, Any, Optional, Union, Tuple, Callable, Iterable

def extract_elements_from_regex_mask(source_to_extract_from: str, reg_mask: str) -> str:
    """
    Extracts elements from a source string based on a regular expression mask.

    :param source_to_extract_from: The source string from which elements will be extracted.
    :param reg_mask: The regular expression pattern to match.
    :return: The matched string based on the regular expression.
    """
    reg_obj = re.compile(reg_mask)
    extracted_ele = reg_obj.search(source_to_extract_from).group(0)
    return extracted_ele


def reverse_n_replace(item: str, replace_from: str, replace_to: str) -> str:
    """
    Reverses a string, performs a replacement, and then reverses it back.

    :param item: The original string to process.
    :param replace_from: The substring to replace.
    :param replace_to: The substring to replace with.
    :return: The modified string after the operations.
    """
    run_1 = item[::-1]
    run_2 = run_1.replace(replace_from, replace_to, 1)
    return run_2[::-1]


def check_for_next_page_request(rownames: List[str], *args: List[Any]) -> List[Any]:
    """
    Checks if a 'next' page request is present in the row names.

    :param rownames: List of row names to check.
    :param args: Additional arguments passed for modification.
    :return: Modified arguments list.
    :raises Exception: If multiple 'next' elements are detected.
    """
    for each_ele in rownames:
        if rownames.count("next") > 1:
            raise Exception("Multiple 'next' detected; use 'next1', 'next2', etc.")
        if 'next' in each_ele:
            get_indx_whr_next_found = rownames.index(each_ele)
            args[0].insert(get_indx_whr_next_found, 'next')
    return args[0]


def get_specefic_subj_value(fs: str, fa: str, ft: str, listx: List[str]) -> str:
    """
    Filters a list based on specific criteria.

    :param fs: First substring to filter.
    :param fa: Second substring to filter.
    :param ft: Third substring to filter.
    :param listx: List of strings to filter from.
    :return: The first matching string or 'N.A.' if not found.
    """
    try:
        l = list(filter(lambda x: fs in x and fa in x and ft in x, listx))
        return l[0]
    except IndexError:
        print(f"{fs}{fa}{ft} image not available")
        return 'N.A.'


def create_column_block(outer_iterator: Iterable[str], inner_iterator: Iterable[str]) -> str:
    """
    Creates a LaTeX column block from given iterators.

    :param outer_iterator: An iterable for outer elements.
    :param inner_iterator: An iterable for inner elements.
    :return: The formatted column block as a string.
    """
    block = r"&"
    for ele_outer in outer_iterator:
        block += (ele_outer + r"&&")
    for ele_inner in inner_iterator:
        if ele_inner in block:
            block = block.replace(ele_inner, "")
    return reverse_n_replace(block, r"&&", r"\\").translate({ord('$'): None}).replace("*", "")


def insert_new_page(colnames: List[str], col_name_block: str, subj: str) -> str:
    """
    Inserts a new page in a LaTeX document.

    :param colnames: List of column names.
    :param col_name_block: Column name block for the LaTeX table.
    :param subj: Subject identifier.
    :return: LaTeX code for the new page.
    """
    return (
        r"\end{tabular}\n"
        r"\newpage\n"
        f"{{\\Large Subject {subj[-2:]}}}\\[0.2cm]\n"
        r"\begin{tabular}{" + "".join(['cc'] * len(colnames)) + r"}\n"
        + col_name_block
    )


def insert_lax_rowname_path_line(
    subj: str, 
    max_height: float, 
    max_width: float, 
    path_extract_func: Callable, 
    *args: Any
) -> str:
    """
    Inserts a LaTeX line for a row name with an image path.

    :param subj: Subject identifier.
    :param max_height: Maximum height of the image in LaTeX.
    :param max_width: Maximum width of the image in LaTeX.
    :param path_extract_func: Function to extract the image path.
    :param args: Additional arguments for path extraction.
    :return: LaTeX code for the row name and image path.
    """
    try:
        return (
            r"\raisebox{-.5\height}{\includegraphics[max height="
            + rf"{max_height}" + r"\textheight,max width="
            + rf"{max_width}" + r"\textwidth]{" 
            + path_extract_func(subj, *args).replace('\\', "/") + r"}}" + r"&&"
        )
    except AttributeError:
        print("""Function returned None. Possible causes:
- Missing template.
- Missing or wrongly numbered images.
- Regex does not match filename, leading to incomplete paths.""")
        exit(1)


def insert_img_filename_line(subj: str, path_extract_func: Callable, *args: Any) -> str:
    """
    Inserts a LaTeX line for an image filename.

    :param subj: Subject identifier.
    :param path_extract_func: Function to extract the image filename.
    :param args: Additional arguments for filename extraction.
    :return: LaTeX code for the image filename.
    """
    raw_filename = path_extract_func(subj, *args).split("\\")[-1][:-4]
    if "dummy" in raw_filename:
        raw_filename = "missing image"
    return r"{\tiny " + raw_filename.replace('_', '\\_') + r"}" + r"&&"






## --------- RANDOM ---------- ##

def validate_random_file(random_file_path: str, subject_list: List[str]) -> List[str]:
    """
    Validates and cleans a random file by comparing its contents against a subject list.

    Args:
        random_file_path (str): The path to the random file to validate.
        subject_list (List[str]): A list of subject IDs.

    Returns:
        List[str]: A cleaned list of strings from the random file, stripped of non-alphanumeric characters.
    """
    # Create a set for the subject list A
    subj_list = []
    for sID in subject_list:
        if sID[-2:][0] != "0":  # If the first digit of the last two numbers of subj ID is non-zero
            subj_list.append(sID[-2:])
        elif sID[-2:][0] == "0":  # If the first digit of the last two numbers of subj ID is zero
            subj_list.append(sID[-1])
        else:
            raise ValueError("Unexpected subject ID format.")

    # Create a set for the random file B
    rand_list = []
    with open(random_file_path) as f:
        lines = f.readlines()
    interesting_lines = lines[5:]
    for line in interesting_lines:
        rand_list.append(line.split("\t")[0])

    # Calculate difference: B - A
    if len(rand_list) > len(subj_list):
        diff_set = set(rand_list) - set(subj_list)
        print(f"Differences found: {diff_set}")
        for diff in diff_set:
            for line in interesting_lines:
                if diff == line.split("\t")[0]:
                    interesting_lines.remove(line)
    else:
        print("No discrepancies found in random file.")

    # Clean and return the remaining lines
    clean_list = []
    for l in interesting_lines:
        stripped = re.sub(r"\W", "", l)
        remove_digits = str.maketrans('', '', digits)
        str_only = stripped.translate(remove_digits)
        clean_list.append(str_only)
    return clean_list


def insert_random_lax_rowname_path_line(spit_out_val: List[str], max_height: float, max_width: float) -> str:
    """
    Inserts a LaTeX line for a row with a random image path.

    Args:
        spit_out_val (List[str]): A list containing paths to image files.
        max_height (float): Maximum height for the image in LaTeX.
        max_width (float): Maximum width for the image in LaTeX.

    Returns:
        str: A formatted LaTeX string.
    """
    return (r"\raisebox{-.5\height}{\includegraphics[max height=" + rf"{max_height}" +
            r"\textheight,max width=" + rf"{max_width}" + r"\textwidth]{" +
            spit_out_val[0].replace('\\', "/") + r"}}" + r"&&")


def insert_random_img_filename_line(spit_out_val: List[str]) -> str:
    """
    Inserts a LaTeX line for a row with the image filename.

    Args:
        spit_out_val (List[str]): A list containing paths to image files.

    Returns:
        str: A formatted LaTeX string for the filename.
    """
    raw_filename = spit_out_val[0].split("\\")[-1][:-4]
    if "dummy" in raw_filename:
        raw_filename = "missing image"

    return r"{\tiny " + raw_filename.replace('_', '\\_') + r"}" + r"&&"


## --------- TO JPG CONVERSION AND RESIZING ---------- ##

def convert_and_scale_to_standard_jpgs(file_extension: str, path_for_validation: str) -> Tuple[str, Optional[List[str]]]:
    """
    Converts and/or resizes image files to standard JPGs.

    Args:
        file_extension (str): The file extension of the images (e.g., 'jpg', 'png', 'tif').
        path_for_validation (str): The path containing the images to be processed.

    Returns:
        Tuple[str, Optional[List[str]]]: The validated path and a list of resized image files, or None if resizing was not required.
    """
    if file_extension == "jpg":
        try:  # Resize only
            validated_path, resized_images = resize_jpg(path_for_validation)
        except TypeError:
            print("Resize limit reached. Total file size less than 400MB and is well-adjusted for PDF use")
            print("Returning original JPG path")
            validated_path = path_for_validation
            resized_images = None
    elif file_extension in {"png", "tif"}:  # Convert and then resize
        validated_path, resized_images = convert_other_extensions_to_jpg(path_for_validation, file_extension)
    return validated_path, resized_images


def convert_other_extensions_to_jpg(path: str, file_type: str) -> Tuple[str, Optional[List[str]]]:
    """
    Converts images of a given type to JPG format.

    Args:
        path (str): The path containing the images to be converted.
        file_type (str): The file type to convert (e.g., 'png', 'tif').

    Returns:
        Tuple[str, Optional[List[str]]]: The path of the converted images and a list of the converted files.
    """
    return jpg_conversion_engine(file_type, path)


def jpg_conversion_engine(ext_type: str, path_to_be_converted: str) -> Tuple[str, Optional[List[str]]]:
    """
    Performs JPG conversion using an external command.

    Args:
        ext_type (str): The type of file to convert (e.g., 'png', 'tif').
        path_to_be_converted (str): The path containing the images to be converted.

    Returns:
        Tuple[str, Optional[List[str]]]: The path of the converted images and a list of the resized files.
    """
    new_jpg_dir = os.path.join(path_to_be_converted, "jpg_converted")
    try:
        os.mkdir(new_jpg_dir)
    except FileExistsError:
        print("File already exists. Returning existing files.")
        return resize_jpg(new_jpg_dir)

    proc = subprocess.Popen(
        f"d: && cd {path_to_be_converted} && magick mogrify -format jpg -depth 8 -path jpg_converted *.{ext_type}",
        shell=True
    )
    print("Converting images to JPG...")
    proc.wait()
    print("Conversion complete!")

    jpg_list = [f for f in os.listdir(new_jpg_dir)]
    if not jpg_list:
        os.rmdir(new_jpg_dir)
        return new_jpg_dir, None
    return resize_jpg(new_jpg_dir)


def resize_jpg(path: str) -> Tuple[str, List[str]]:
    """
    Resizes JPG images to a smaller size if needed.

    Args:
        path (str): The path containing the JPG images.

    Returns:
        Tuple[str, List[str]]: The path of the resized images and a list of the resized files.
    """
    total_size = 0
    sub_1_count = 0
    check_list = []
    sub1_file_check_mask = re.compile(r"S001F[0-9]{2}T[0-9]{2}")

    for f in os.listdir(path):
        if f.endswith("jpg") and isinstance(f, str):
            check_list.append(f)
            total_size += os.path.getsize(os.path.join(path, f))

    for f in os.listdir(path):
        try:
            if f.endswith("jpg") and sub1_file_check_mask.search(f):
                sub_1_count += 1
        except AttributeError:
            break

    print(total_size / 1024 ** 2)
    print(sub_1_count)
    thresh = get_resize_percentage(total_size, sub_1_count)
    if thresh is None:
        print("File size less than 400MB")
        raise TypeError
    small_jpg_dir = os.path.join(path, f"jpg_small{thresh[:-1]}")
    try:
        os.mkdir(small_jpg_dir)
    except FileExistsError:
        small_jpg_list = [f for f in os.listdir(small_jpg_dir)]
        return small_jpg_dir, small_jpg_list

    proc = subprocess.Popen(
        f"d: && cd {path} && magick mogrify -resize {thresh} -path jpg_small{thresh[:-1]} *.jpg",
        shell=True
    )
    print(f"Resizing images to {thresh}...")
    proc.wait()
    small_jpg_list = [f for f in os.listdir(small_jpg_dir)]
    if not small_jpg_list:
        os.rmdir(small_jpg_dir)
    return small_jpg_dir, small_jpg_list


def get_resize_percentage(total_imgs_size: float, sub1_counter: int) -> Optional[str]:
    """
    Determines the resize percentage for images based on total size and subject count.

    Args:
        total_imgs_size (float): The total size of the images in bytes.
        sub1_counter (int): The count of Subject1 images.

    Returns:
        Optional[str]: The resize percentage as a string, or None if resizing is not needed.
    """
    my_dict = {
        500: {1: "50%", 0.5: "45%", 0: "40%"},
        450: {1: "45%", 0.5: "40%", 0: "30%"},
        400: {1: "40%", 0.5: "35%", 0: "30%"}
    }
    for limit in my_dict.keys():
        if (total_imgs_size / 1024 ** 2) >= limit:
            for threshold in my_dict[limit].keys():
                if (sub1_counter / 10) >= threshold:
                    return my_dict[limit][threshold]
    return None

## --------- MISSING FILES HANDLER ---------- ##

def data_preprocessing() -> None:
    """Placeholder function for data preprocessing tasks."""
    pass


def create_blank_dummy(height: int, width: int, dummy_filepath: str) -> None:
    """
    Creates a resized dummy image from a reference image and saves it to the specified path.

    Args:
        height (int): Height of the dummy image.
        width (int): Width of the dummy image.
        dummy_filepath (str): File path to save the dummy image.
    """
    image = cv2.imread(r"path_to_missing_image_replacement_image\source\bin\missing_pic.jpg")
    dim = (width, height)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    cv2.imwrite(dummy_filepath, resized)


def get_image_properties(image_path: str) -> Tuple[int, int]:
    """
    Extracts the height and width of an image.

    Args:
        image_path (str): File path to the image.

    Returns:
        Tuple[int, int]: Height and width of the image.
    """
    im = cv2.imread(image_path)
    height = im.shape[0]
    width = im.shape[1]
    return height, width


def make_dict_with_barcode_as_keys(list_w_filepaths: List[str]) -> Dict[Tuple[str, str, str], str]:
    """
    Creates a dictionary with barcodes as keys and file paths as values.

    Args:
        list_w_filepaths (List[str]): List of file paths.

    Returns:
        Dict[Tuple[str, str, str], str]: Dictionary with barcodes as keys and file paths as values.
    """
    Subj_mask = re.compile(r'S[0-9]{3}')
    Area_mask = re.compile(r'F[0-9]{2}')
    Time_mask = re.compile(r'T[0-9]{2}')
    barcode_dict = {}

    for fpath in list_w_filepaths:
        barcode_dict[(Subj_mask.search(fpath.split("\\")[-1]).group(0),
                      Area_mask.search(fpath.split("\\")[-1]).group(0),
                      Time_mask.search(fpath.split("\\")[-1]).group(0))] = fpath
    return barcode_dict


def get_barcode_groups(filepath_list: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Groups barcodes (subject, area, time) from file paths.

    Args:
        filepath_list (List[str]): List of file paths.

    Returns:
        Tuple[List[str], List[str], List[str]]: Sorted unique lists of subjects, areas, and times.
    """
    Subj_mask = re.compile(r'S[0-9]{3}')
    Area_mask = re.compile(r'F[0-9]{2}')
    Time_mask = re.compile(r'T[0-9]{2}')

    subj_grp, area_grp, time_grp = [], [], []

    for fpath in filepath_list:
        fpath_str_list = fpath.split('\\')

        subj_grp.append(Subj_mask.search(fpath_str_list[-1]).group(0))
        area_grp.append(Area_mask.search(fpath_str_list[-1]).group(0))
        time_grp.append(Time_mask.search(fpath_str_list[-1]).group(0))

    subj_grp_sorted = sorted(set(subj_grp))
    area_grp_sorted = sorted(set(area_grp))
    time_grp_sorted = sorted(set(time_grp))

    return subj_grp_sorted, area_grp_sorted, time_grp_sorted


def find_missing_barcodes(filepath_list: List[str]) -> List[Tuple[str, str, str]]:
    """
    Identifies missing barcodes by comparing expected combinations of subject, area, and time with existing keys.

    Args:
        filepath_list (List[str]): List of file paths.

    Returns:
        List[Tuple[str, str, str]]: List of missing barcode combinations.
    """
    barc_dict = make_dict_with_barcode_as_keys(filepath_list)
    missing_list = []

    s_grp, a_grp, t_grp = get_barcode_groups(filepath_list)
    for subj in s_grp:
        for area in a_grp:
            for time in t_grp:
                if (subj, area, time) not in barc_dict.keys():
                    missing_list.append((subj, area, time))

    return missing_list


def replace_missing_barcodes_with_dummy(list_with_filepaths: List[str], visia_flag: int = 0) -> List[str]:
    """
    Replaces missing barcode combinations with dummy images.

    Args:
        list_with_filepaths (List[str]): List of file paths.
        visia_flag (int): Flag indicating if VISIA-specific images are handled (default is 0).

    Returns:
        List[str]: List of paths to generated dummy images.
    """
    missing_list = find_missing_barcodes(list_with_filepaths)
    if len(missing_list) == 0:
        print("NO MISSING VALUES FOUND...None is returned")
        input("Press Enter to proceed...")
        return []

    print("Missing values found...Please check log file and adjust tex file accordingly.")
    input("Press Enter to proceed...")
    Subj_mask = re.compile(r'S[0-9]{3}')
    Area_mask = re.compile(r'F[0-9]{2}')
    Time_mask = re.compile(r'T[0-9]{2}')
    Light_mask = re.compile(r'(T[0-9]{2})([A-Za-z0-9]{4})')
    dummy_path_list = []
    
    for ids_tup in missing_list:
        first_path_as_sample = list_with_filepaths[0]
        image_name = first_path_as_sample.split("\\")[-1]
        old_subj_id = Subj_mask.search(image_name).group(0)
        old_area_id = Area_mask.search(image_name).group(0)
        old_time_id = Time_mask.search(image_name).group(0)

        if visia_flag == 1:
            light_codes = ["STD1", "STD2", "UVNF", "XPOL", "PPOL", "UVFF"]
            light_codes_actual = set([lc for fp in list_with_filepaths for lc in light_codes if lc in fp.split("\\")[-1]])
            for light_name in light_codes_actual:
                old_light_id = Light_mask.search(image_name).group(2)
                dummy_name = image_name.replace(old_subj_id, ids_tup[0]).replace(old_area_id, ids_tup[1]).replace(old_time_id, ids_tup[2]).replace(old_light_id, light_name)
                dummy_path = first_path_as_sample.replace(image_name, dummy_name.replace(".jpg", "_dummy.jpg"))
                h, w = get_image_properties(first_path_as_sample)
                create_blank_dummy(h, w, dummy_path)
                dummy_path_list.append(dummy_path)
        else:
            dummy_name = image_name.replace(old_subj_id, ids_tup[0]).replace(old_area_id, ids_tup[1]).replace(old_time_id, ids_tup[2])
            dummy_path = first_path_as_sample.replace(image_name, dummy_name.replace(".jpg", "_dummy.jpg"))
            h, w = get_image_properties(first_path_as_sample)
            create_blank_dummy(h, w, dummy_path)
            dummy_path_list.append(dummy_path)

    return dummy_path_list


## --------- FINAL DATASET CLEAN BEFORE LATEX ---------- ##

def remove_redundant_jpgs(val_path: str) -> None:
    """
    Removes redundant JPEG files from a directory, excluding those in a specific subdirectory.

    Args:
        val_path (str): Path to the directory containing JPEG files.
    """
    split_path = val_path.split("\\")
    if split_path[-1] != "jpg_converted":
        for fn in os.listdir("\\".join(split_path[:-1])):
            if fn.endswith(".jpg"):
                os.remove(os.path.join("\\".join(split_path[:-1]), fn))
    else:
        print("No JPGsmall dir exists; just the jpg_converted dir exists; no further scaling was done")


def remove_counter_from_filenames(val_path: str) -> None:
    """
    Removes counters from filenames matching a specific pattern.

    Args:
        val_path (str): Path to the directory containing the files.
    """
    tmp_rgx0 = r"S[0-9]{3}F[0-9]{2}T[0-9]{2}[a-zA-Z0-9]*"
    tmp_rgx1 = r"[0-9]{4}"
    for fn in os.listdir(val_path):
        try:
            if re.match(tmp_rgx0, fn.split("_")[0]) is not None and re.match(tmp_rgx1, fn.split("_")[1]):
                clean_fn = fn.replace("_" + re.match(tmp_rgx1, fn.split("_")[1]).group(0), "")
                print(f"Renaming {fn} to {clean_fn}")
                os.rename(os.path.join(val_path, fn), os.path.join(val_path, clean_fn))
        except IndexError:
            print("Counters already removed")
            break


def remove_bitmaps_from_tif_conversion(val_path: str) -> None:
    """
    Removes bitmap artifacts generated during TIFF-to-JPEG conversion.

    Args:
        val_path (str): Path to the directory containing the files.
    """
    tmp_rgx0 = r"S[0-9]{3}F[0-9]{2}T[0-9]{2}[a-zA-Z0-9]*"

    for fn in os.listdir(val_path):
        try:
            if re.match(tmp_rgx0, fn.split("-")[0]) is not None and fn.split("-")[1] == "0.jpg":
                clean_fn = fn.replace("-0.jpg", ".jpg")
                print(f"Renaming {fn} to {clean_fn}")
                os.rename(os.path.join(val_path, fn), os.path.join(val_path, clean_fn))
            elif re.match(tmp_rgx0, fn.split("-")[0]) is not None and fn.split("-")[1] == "1.jpg":
                print(f"{fn} deleted")
                os.remove(os.path.join(val_path, fn))
        except IndexError:
            print("Bitmaps already removed")
            break


def archive_data(validated_path: str, studynumber: str, Test_type: str, file_extension: str) -> None:
    """
    Archives test data by moving files to a designated directory and deleting unnecessary files.

    Args:
        validated_path (str): Path to the validated data directory.
        studynumber (str): Study number associated with the test.
        Test_type (str): Type of the test conducted.
        file_extension (str): File extension (e.g., "pdf", "tex") to archive.
    """
    # Deleting unnecessary files
    for f in os.listdir(os.getcwd()):
        if f.endswith(("gz", "log", "aux", "out")):
            os.remove(os.path.join(os.getcwd(), f))
            print(f"{f} deleted")

    test_folder_path = os.path.join(validated_path, "Test_results")
    if not os.path.isdir(test_folder_path):
        os.mkdir(test_folder_path)

    move_list = []
    for f in os.listdir(os.getcwd()):
        descp_folder = r"path_to_project\DESCPR_files"
        if f.endswith("docx") or (f.endswith("tex") and "with" not in f and "description" in f):
            shutil.move(os.path.join(os.getcwd(), f), os.path.join(descp_folder, f))
        elif f.endswith(("pdf", "tex", "xlsx")) or (f.endswith(".txt") and "missing" in f):
            move_list.append(f)

    # Archiving all files into the study folder "Test_results" within the images folder
    if len(move_list) > 0:
        while True:
            archive_approval = input("Would you like to archive the files for this test (y/n): ")
            if archive_approval.lower() == "y":
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                new_folderpath = os.path.join(test_folder_path, f"{studynumber}_{Test_type}_{file_extension}__{timestamp}")
                os.mkdir(new_folderpath)
                for selected_file in move_list:
                    shutil.move(os.path.join(os.getcwd(), selected_file), os.path.join(new_folderpath, selected_file))
                    print(f"{selected_file} moved to subfolder - {studynumber}_{Test_type}_{file_extension}__{timestamp} inside folder - Test_results")
                
                # Open the folder and latest files for review
                subprocess.Popen(f"start {new_folderpath} && pause", shell=True)
                pdf_files = glob.glob(new_folderpath + "\\*pdf")
                latex_files = glob.glob(new_folderpath + "\\*tex")
                try:
                    max_file_pdf = max(pdf_files, key=os.path.getctime, default=None)
                    max_file_latex = max(latex_files, key=os.path.getctime, default=None)

                    if max_file_pdf or max_file_latex:
                        if max_file_latex and not max_file_pdf:
                            subprocess.Popen(f"d: && start {max_file_latex} && pause", shell=True).wait()
                        elif max_file_pdf:
                            subprocess.Popen(f"d: && start {max_file_pdf} && start {max_file_latex} && pause", shell=True).wait()
                        print("Goodbye")
                        break
                except ValueError:
                    print("No PDF or LaTeX file found.")
                    print("Goodbye")
                    break
            elif archive_approval.lower() == "n":
                print("Archiving skipped.")
                break
