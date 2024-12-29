"""
Program that checks images for errors in filenames using the timestamp and barcode string literals.
Errors detected may fall under the following categories:
- Timepoints are checked for homogeneity with date(timestamp)
- Unexpected Subject changes
- Unexpected Side changes
- Missing Values 
- Duplicates

conda env:
conda activate env_image_processing
"""

from pathlib import Path
import os
import time
import shutil
import sys
from typing import List, Dict, Tuple, Optional

from Excel_logging import log_to_excel_and_flag_outliers
from Visuals_Stable import vis_data_and_display, visualize_timestamp_per_folder
from Common_functions import (
    check_for_side_consistency_and_duplicates, get_time_sorted_filelist_from_basepath,
    check_timeIDs_against_timestamp, move_duplicates_to_superseded_folder,
    create_ref_dict, get_cleaned_files_with_small_deltas, populate_missing_value_folder,
    create_new_dict_after_filename_change, get_corrected_filenames, find_delta,
    correct_wrong_fname
)

TESTING = True  # Set to False once program is tested and finalized
FILE_EXTENSION = '.jpg'
BASE_PATHNAME = Path(r'Path to image folder')

FLAGGED_PATH = BASE_PATHNAME / "flagged"
TIME_DUP_PATH = BASE_PATHNAME / "time_duplicates"
MISSING_PATH = BASE_PATHNAME / "missing"
WRONG_SIDE_LABEL_PATH = BASE_PATHNAME / "wrong_side_label"
DUPL_FOLDER = BASE_PATHNAME / "superseded"

EXCEL_VALID_DICT = {
    "dups_less_than": 1,
    "dups_or_sidechange_less_than": 2,
    "range_more_than": 2,
    "range_less_than": 5,
    "subjchange_more_than": 3,
}

SMALL_DELTA_VAL_CHECK = 1  # for detecting hidden duplicates

def handle_time_duplicates(time_duplicates: Optional[List[Tuple[str, str]]], base_path: Path) -> None:
    """Handle images with the same timestamps."""
    if time_duplicates:
        os.mkdir(TIME_DUP_PATH)
        for dupl_tuple in time_duplicates:
            shutil.move(base_path / dupl_tuple[0], TIME_DUP_PATH)

def handle_subject_changes(delta_list: List[Tuple], base_path: Path, flagged_path: Path) -> Dict:
    """Handle and log subject changes."""
    excelfile_path = base_path / "timestamp_logs.xlsx"
    flagged_ref_dict = {}
    flagged_ref_dict = log_to_excel_and_flag_outliers(delta_list, excelfile_path, base_path, flagged_path, flagged_ref_dict, EXCEL_VALID_DICT)
    if flagged_path.is_dir():
        visualize_timestamp_per_folder(flagged_path)
    return flagged_ref_dict

def handle_filename_changes(flagged_path: Path, flagged_ref_dict: Dict, base_path: Path) -> None:
    """Handle filename changes due to subject changes."""
    while True:
        rename_check = input("Have you renamed any images due to subject changes? (y/n) ").lower()
        if rename_check == "y":
            modified_ref_dict = create_new_dict_after_filename_change(flagged_path)
            corrected_filename_list = get_corrected_filenames(modified_ref_dict, flagged_ref_dict)
            for tupl in corrected_filename_list:
                correct_wrong_fname(tupl, base_path)
            break
        elif rename_check == "n":
            print("User says no changes were made. Ending Program")
            if flagged_path.is_dir():
                shutil.rmtree(flagged_path)
            sys.exit(0)

def handle_wrong_side_labeling(base_path: Path, wrong_side_label_path: Path) -> None:
    """Handle wrong side labeling."""
    get_cleaned_files_with_small_deltas(base_path, wrong_side_label_path, FILE_EXTENSION)
    flagged_ref_dict = create_ref_dict({}, wrong_side_label_path)
    if wrong_side_label_path.is_dir():
        visualize_timestamp_per_folder(wrong_side_label_path)
    
    while True:
        rename_check = input("Have you renamed the wrong image? (y/n) ").lower()
        if rename_check == "y":
            modified_ref_dict = create_ref_dict({}, wrong_side_label_path)
            corrected_filename_list = get_corrected_filenames(modified_ref_dict, flagged_ref_dict)
            for tupl in corrected_filename_list:
                correct_wrong_fname(tupl, base_path)
            if wrong_side_label_path.is_dir():
                shutil.rmtree(wrong_side_label_path)
            break
        elif rename_check == "n":
            print("Prematurely Terminating Program due to user request")
            sys.exit(0)

def handle_missing_values(base_path: Path, missing_path: Path, missing_values: List[str]) -> None:
    """Handle missing values."""
    if missing_values:
        for val in missing_values:
            print(f"Missing value: {val}")
        
        if missing_path.is_dir():
            shutil.rmtree(missing_path)
        missing_path.mkdir(exist_ok=True)
        
        populate_missing_value_folder(missing_path, base_path, missing_values)
        flagged_ref_dict = create_ref_dict({}, missing_path)
        visualize_timestamp_per_folder(missing_path)
        
        while True:
            rename_check = input("Have you renamed the duplicate missing image? (y/n) ").lower()
            if rename_check == "y":
                modified_ref_dict = create_ref_dict({}, missing_path)
                corrected_filename_list = get_corrected_filenames(modified_ref_dict, flagged_ref_dict)
                for tupl in corrected_filename_list:
                    correct_wrong_fname(tupl, base_path)
                if missing_path.is_dir():
                    shutil.rmtree(missing_path)
                break
    else:
        print("No missing values found. Continuing...")
        time.sleep(2)

def main():
    """Main function to process and check image files."""
    file_list_sorted = get_time_sorted_filelist_from_basepath(BASE_PATHNAME, FILE_EXTENSION)
    saved_cnt, _ = vis_data_and_display(file_list_sorted, BASE_PATHNAME, 0, FILE_EXTENSION)

    if FLAGGED_PATH.is_dir():
        shutil.rmtree(FLAGGED_PATH)

    delta_list, time_duplicates = find_delta(file_list_sorted)
    handle_time_duplicates(time_duplicates, BASE_PATHNAME)

    time_id_dict = check_timeIDs_against_timestamp(file_list_sorted)
    print(time_id_dict)
    if len(time_id_dict) > 1:
        input("There's more than one timestamp in this folder, adjust the time ids and then press enter")
    else:
        input("Times are cleaned. Press Enter to proceed")

    flagged_ref_dict = handle_subject_changes(delta_list, BASE_PATHNAME, FLAGGED_PATH)
    handle_filename_changes(FLAGGED_PATH, flagged_ref_dict, BASE_PATHNAME)

    if FLAGGED_PATH.is_dir():
        shutil.rmtree(FLAGGED_PATH)

    handle_wrong_side_labeling(BASE_PATHNAME, WRONG_SIDE_LABEL_PATH)

    _, missing_values, _ = check_for_side_consistency_and_duplicates(BASE_PATHNAME, FILE_EXTENSION)
    handle_missing_values(BASE_PATHNAME, MISSING_PATH, missing_values)

    duplicates, _, _ = check_for_side_consistency_and_duplicates(BASE_PATHNAME, FILE_EXTENSION)
    raw_files_missing = move_duplicates_to_superseded_folder(duplicates, BASE_PATHNAME)
    for raw_val in raw_files_missing:
        print(f"The following raw files are missing: {raw_val}")

if __name__ == '__main__':
    main()
    input("Finish Analysis? Press Enter ")
    if not TESTING:
        if DUPL_FOLDER.is_dir():
            for file in os.listdir(DUPL_FOLDER):
                shutil.move(DUPL_FOLDER / file, BASE_PATHNAME)
            if not os.listdir(DUPL_FOLDER):
                shutil.rmtree(DUPL_FOLDER)
            else:
                print("Folder not empty")
