
import os
import exifread
import datetime
import os
import sys
from typing import List, Tuple, Dict, Set, Optional
from pathlib import Path
import re
import shutil
import numpy as np
from collections import OrderedDict
from sklearn.cluster import KMeans
from ordered_set import OrderedSet

def get_original_time_from_exif(filename: str, main_study_path: str) -> Optional[str]:
    """
    Retrieve original "image taken" timestamp from the file metadata/exif.

    Args:
        filename (str): The name of the image file.
        main_study_path (str): The path to the root study folder.

    Returns:
        Optional[str]: The timestamp in the format '%Y:%m:%d %H:%M:%S' if found, None otherwise.

    Raises:
        SystemExit: If the timestamp is not found in the image metadata.
    """
    abs_path_to_image = os.path.join(main_study_path, filename)
    
    with open(abs_path_to_image, 'rb') as f:
        tags = exifread.process_file(f)
    
    for tag in tags.keys():
        if tag == 'Image DateTime':
            return str(tags[tag])
    
    print("Date is still None. Exiting")
    sys.exit()

def get_time_sorted_filelist_from_basepath(main_study_path: Path, file_ext: str) -> List[Tuple[str, str]]:
    """
    Get a list of filenames and times, sorted according to their timestamps.

    Args:
        main_study_path (Path): The path to the root study folder.
        file_ext (str): Image extension to be detected (e.g., '.jpg').

    Returns:
        List[Tuple[str, str]]: Time sorted list with (filenames and timestamp) tuples.
    """
    file_list = [
        (entry.name, get_original_time_from_exif(entry.name, main_study_path))
        for entry in main_study_path.iterdir()
        if entry.is_file() and entry.suffix == file_ext
    ]
    return sorted(file_list, key=lambda x: x[1])

def check_for_side_consistency_and_duplicates(main_study_path: Path, file_ext: str) -> Tuple[List[Tuple[str, str]], List[str], List[Tuple[str, str]]]:
    """
    Check for side consistency and duplicates in the image files.

    Args:
        main_study_path (Path): The path to the root study folder.
        file_ext (str): Image extension to be detected (e.g., '.jpg').

    Returns:
        Tuple[List[Tuple[str, str]], List[str], List[Tuple[str, str]]]: 
            - duplicate list
            - missing files list
            - clean file list
    """
    subj_mask = re.compile(r"S[0-9]{3}")
    area_mask = re.compile(r"F[0-9]{2}")
    time_mask = re.compile(r"T[0-9]{2}")

    clean_file_list = get_time_sorted_filelist_from_basepath(main_study_path, file_ext)
    
    subj_set = set()
    area_set = set()
    time_set = set()

    for f_element, _ in clean_file_list:
        if f_element.endswith(file_ext):
            subj_set.add(subj_mask.search(f_element).group(0))
            area_set.add(area_mask.search(f_element).group(0))
            time_set.add(time_mask.search(f_element).group(0))

    duplicate_list = []
    missing_list = []

    for subj_id in subj_set:
        for area_id in area_set:
            for time_id in time_set:
                matching_files = [
                    item for item in clean_file_list
                    if all(id in item[0] for id in (subj_id, area_id, time_id))
                ]
                if len(matching_files) > 1:
                    duplicate_list.extend(matching_files[:-1])
                elif not matching_files:
                    missing_list.append(f"{subj_id}{area_id}{time_id} missing")

    return duplicate_list, missing_list, clean_file_list

 
def check_timeIDs_against_timestamp(time_sorted_file_list):
    """
    Compares each time ID(e.g. T01, T02) with its respective timestamp date and returns (TID, date, date counts) 

        :param main_study_path: path to root study folder
        :type main_study_path: str
        :return: a dictionary containing {TID : (date, date counts)} 
        :rtype: dict
    """

    # time_sorted_file_list = get_time_sorted_filelist_from_basepath(main_study_path, file_ext)

    T_id_mask = re.compile(r"T[0-9]{2}")
    # time_ID_dict = {}

    T_id_list = [T_id_mask.search(ele[0]).group(0) for ele in time_sorted_file_list]
    dates_list = [datetime.datetime.strptime(ele[-1], '%Y:%m:%d %H:%M:%S').date() for ele in time_sorted_file_list]

    T_id_set = OrderedSet(T_id_list)
    dates_set = OrderedSet(dates_list)
        
    # checking if number of ids match the number of dates
    T_id_dict = {}
    dates_dict = {}

    # creates dicts for individual counts 
    for T_id in T_id_set:
        T_id_dict[T_id] = T_id_list.count(T_id)
       

    for d in  dates_set:
        dates_dict[d] = dates_list.count(d)

    if len(T_id_dict) == len(dates_dict):

        # creating the "T_id-Date-Count" tuple 
        t_id_validation_dict = {}
        for t_id_key, d_key in zip(T_id_dict.keys(), dates_dict.keys()):
            t_id_validation_dict[t_id_key] = (d_key, dates_dict[d_key])

        return t_id_validation_dict
    
    elif len(T_id_dict) != len(dates_dict): 
        t_id_validation_dict = {}
        for t_id_key in T_id_dict.keys():
            for d_key in dates_dict.keys():
                for ele in time_sorted_file_list:
                    if t_id_key == T_id_mask.search(ele[0]).group(0):
                        t_id_validation_dict[t_id_key] = ((t_id_key, T_id_dict[t_id_key]), (d_key, dates_dict[d_key]))
        return t_id_validation_dict


def find_delta(original_list_with_times: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str, str, str, int]], Optional[List[Tuple[str, str]]]]:
    """
    Find the difference (delta) between file timestamps.

    Args:
        original_list_with_times (List[Tuple[str, str]]): List containing files and their corresponding timestamps.

    Returns:
        Tuple[List[Tuple[str, str, str, str, int]], Optional[List[Tuple[str, str]]]]:
            - List containing tuples with current, previous file, corresponding times and the delta.
            - List containing filenames with time duplicates (or None if no duplicates).
    """
    list_with_deltas = []
    timestamp_duplicates = None
    previous_val = previous_file = None

    for i, (current_file, current_val) in enumerate(original_list_with_times):
        if i == 0:
            previous_val = current_val
            previous_file = current_file
        else:
            previous_val = original_list_with_times[i-1][1]
            previous_file = original_list_with_times[i-1][0]

        if current_val == previous_val:
            timestamp_duplicates = timestamp_duplicates or []
            timestamp_duplicates.append((current_file, current_val))
            continue

        delta = datetime.datetime.strptime(current_val, '%Y:%m:%d %H:%M:%S') - datetime.datetime.strptime(previous_val, '%Y:%m:%d %H:%M:%S')
        list_with_deltas.append((current_file, previous_file, str(current_val), str(previous_val), delta.seconds))

    return list_with_deltas, timestamp_duplicates

def get_cleaned_files_with_small_deltas(base_path: Path, path_to_wrong_side_labels: Path, file_ext: str) -> None:
    """
    Process files to identify and handle duplicates and small time deltas.

    Args:
        base_path (Path): Path to the base directory.
        path_to_wrong_side_labels (Path): Path to store wrong side labels.
        file_ext (str): File extension to process.
    """
    dup_list, _, cleaned_again_list = check_for_side_consistency_and_duplicates(base_path, file_ext)
    new_delta_list, _ = find_delta(cleaned_again_list)
    
    dup_list = [dup[0] for dup in dup_list]
    rgx_mask = r"S[0-9]{3}F[0-9]{2}"
    tuple_dups = [delta_ele for n, delta_ele in enumerate(new_delta_list[1:], 1) 
                  if any(retrieve_id_mask(rgx_mask, delta_ele[0]) in dup for dup in dup_list)]

    if not dup_list:
        print("No duplicates were found. Duplicate list returned empty")
    elif len(dup_list) > 3:
        handle_multiple_duplicates(tuple_dups, path_to_wrong_side_labels, base_path, cleaned_again_list)
    else:
        handle_few_duplicates(tuple_dups, path_to_wrong_side_labels, base_path, cleaned_again_list)

def handle_multiple_duplicates(tuple_dups: List[Tuple], path_to_wrong_side_labels: Path, base_path: Path, cleaned_again_list: List[Tuple[str, str]]) -> None:
    """
    Handle cases with multiple duplicates.

    Args:
        tuple_dups (List[Tuple]): List of duplicate tuples.
        path_to_wrong_side_labels (Path): Path to store wrong side labels.
        base_path (Path): Path to the base directory.
        cleaned_again_list (List[Tuple[str, str]]): Cleaned list of files.
    """
    path_to_wrong_side_labels.mkdir(exist_ok=True)
    ord_tupl_dict = OrderedDict((tup[-1], tup) for tup in tuple_dups)
    data_dups = np.array(list(ord_tupl_dict.keys()))
    
    mean_clean, med_clean, iqr_clean = remove_outliers_from_array(data_dups)
    
    for n, cleaned_array in enumerate([mean_clean, med_clean, iqr_clean], start=1):
        get_kmeans_clusters(cleaned_array, base_path, n)
    
    median_dup = np.median(sorted(data_dups))
    outlier_data = data_dups[data_dups >= median_dup]
    clean_tup_dup = [ord_tupl_dict[out] for out in outlier_data]
    fil_clean_tuple_dups = filtered_duplicates_mask(retrieve_id_mask, clean_tup_dup)
    copy_wrong_sidenames(fil_clean_tuple_dups, path_to_wrong_side_labels, base_path, cleaned_again_list)

def handle_few_duplicates(tuple_dups: List[Tuple], path_to_wrong_side_labels: Path, base_path: Path, cleaned_again_list: List[Tuple[str, str]]) -> None:
    """
    Handle cases with few duplicates.

    Args:
        tuple_dups (List[Tuple]): List of duplicate tuples.
        path_to_wrong_side_labels (Path): Path to store wrong side labels.
        base_path (Path): Path to the base directory.
        cleaned_again_list (List[Tuple[str, str]]): Cleaned list of files.
    """
    fil_tuple_dups = filtered_duplicates_mask(retrieve_id_mask, tuple_dups)
    copy_wrong_sidenames(fil_tuple_dups, path_to_wrong_side_labels, base_path, cleaned_again_list)



def create_new_dict_after_filename_change(flagged_folder_pathname: Path) -> Dict[str, Tuple[str, ...]]:
    """
    Creates a new dictionary and populates it with filenames from the modified state of the analyzed folder.

    Args:
        flagged_folder_pathname (Path): Path where the flagged files are stored.

    Returns:
        Dict[str, Tuple[str, ...]]: Dictionary with folder names as keys and filenames as values.
    """
    modified_dict = {}
    for current_folder_path, _, fnames in os.walk(flagged_folder_pathname):
        if fnames:
            folder_key = current_folder_path.split(os.sep)[-1]
            modified_dict[folder_key] = tuple(fnames)
    return modified_dict

def get_corrected_filenames(modified_dict_to_compare: Dict[str, Tuple[str, ...]], 
                            flagged_reference_dict: Dict[str, Tuple[str, ...]]) -> List[Tuple[str, str]]:
    """
    Finds the files that have been renamed by the user in the analysis folder.

    Args:
        modified_dict_to_compare (Dict[str, Tuple[str, ...]]): Dictionary containing values after filename changes.
        flagged_reference_dict (Dict[str, Tuple[str, ...]]): Dictionary containing values before filename changes.

    Returns:
        List[Tuple[str, str]]: List containing the corrected filenames (old_name, new_name).
    """
    list_of_corrected_fnames = []
    
    if set(modified_dict_to_compare.keys()) != set(flagged_reference_dict.keys()):
        print("Sets are not equal. Something went wrong. Quitting.")
        return list_of_corrected_fnames

    for key in modified_dict_to_compare.keys():
        old_value = set(flagged_reference_dict[key]) - set(modified_dict_to_compare[key])
        new_value = set(modified_dict_to_compare[key]) - set(flagged_reference_dict[key])
        if old_value and new_value:
            list_of_corrected_fnames.append((old_value.pop(), new_value.pop()))

    if not list_of_corrected_fnames:
        print("No filename changes made. Continuing...")

    return list_of_corrected_fnames

def correct_wrong_fname(tpl_with_old_new_names: Tuple[str, str], main_study_path: Path) -> None:
    """
    Rename file in the main folder as per changes made by the user after analysis/review in the analysis folder.

    Args:
        tpl_with_old_new_names (Tuple[str, str]): Tuple containing (old_name, new_name).
        main_study_path (Path): Path to root study folder.
    """
    old_name, new_name = tpl_with_old_new_names
    try:
        (main_study_path / old_name).rename(main_study_path / new_name)
    except FileNotFoundError:
        print("File not found. Check filenames again.")

    try:
        old_raw = old_name.replace(".jpg", ".cr2")
        new_raw = new_name.replace(".jpg", ".cr2")
        (main_study_path / old_raw).rename(main_study_path / new_raw)
    except FileNotFoundError:
        print(f"No raw file for {new_name} exists in the main folder.")

def move_duplicates_to_superseded_folder(duplicates_list: List[Tuple[str, str]], main_study_path: Path) -> List[str]:
    """
    Creates folder "superseded" and moves duplicates to this folder.

    Args:
        duplicates_list (List[Tuple[str, str]]): List containing possible duplicate filenames and their timestamps.
        main_study_path (Path): Path to root study folder.

    Returns:
        List[str]: List of raw files not found in the main folder.
    """
    duplicates_folder_path = main_study_path / "superseded"
    duplicates_folder_path.mkdir(exist_ok=True)

    raw_not_found_list = []
    for dup_file, time in duplicates_list:
        shutil.move(str(main_study_path / dup_file), str(duplicates_folder_path))
        print(f"{dup_file} with {time} moved to 'superseded' folder")

        file_to_move_cr2 = dup_file.replace(".jpg", ".cr2")
        cr2_path = main_study_path / file_to_move_cr2
        if cr2_path.is_file():
            shutil.move(str(cr2_path), str(duplicates_folder_path))
        else:
            print(f"The raw image - {file_to_move_cr2} does not exist in the main study folder")
            raw_not_found_list.append(file_to_move_cr2)

    return raw_not_found_list


def create_ref_dict(wrong_name_path: Path) -> Dict[str, List[str]]:
    """
    Creates a reference dictionary that holds original unchanged values before user analysis.

    Args:
        wrong_name_path (Path): Path to folder which is to be referenced.

    Returns:
        Dict[str, List[str]]: Reference dictionary with old values.
    """
    flagged_ref_dict = {}
    try:
        for folder in wrong_name_path.iterdir():
            if folder.is_dir():
                flagged_ref_dict[folder.name] = [file.name for file in folder.iterdir() if file.is_file()]
        return flagged_ref_dict
    except FileNotFoundError:
        print("No duplicates exist. Wrong side label folder was not created.")
        return {}

def populate_missing_value_folder(missing_value_path: Path, main_study_path: Path, missing_value_list: List[str]) -> None:
    """
    Moves missing files to missing value folder.

    Args:
        missing_value_path (Path): Path to folder where missing values are stored.
        main_study_path (Path): Path to root study folder.
        missing_value_list (List[str]): List containing the missing files.
    """
    missing_subj_folder_set = set(value[:4] for value in missing_value_list)

    for subj_id in missing_subj_folder_set:
        for file in main_study_path.glob(f"{subj_id}*.jpg"):
            subj_fold_path = missing_value_path / subj_id
            subj_fold_path.mkdir(exist_ok=True)
            shutil.copy2(file, subj_fold_path)

def flag_suspicious_files(flagged_folder: Path, main_folder: Path, tuple_with_deltas: Tuple[str, ...], 
                          suffix: str, refrnce_set: Set[str]) -> Dict[str, Set[str]]:
    """
    Groups suspicious files according to their subject_ids in separate subfolders inside the flagged parent folder.

    Args:
        flagged_folder (Path): Path to flagged folder.
        main_folder (Path): Path to root folder.
        tuple_with_deltas (Tuple[str, ...]): Tuple containing the suspicious/flagged delta values.
        suffix (str): Appends to subject id for the folder name.
        refrnce_set (Set[str]): Set of reference values.

    Returns:
        Dict[str, Set[str]]: Suspicious folder dictionary filled with values of interest.
    """
    flagged_folder.mkdir(exist_ok=True)
    trimmed_filename = tuple_with_deltas[0].replace(".jpg", "")
    suspicious_folder = flagged_folder / f"{trimmed_filename}_{suffix}"
    suspicious_folder.mkdir(exist_ok=True)

    shutil.copy2(main_folder / tuple_with_deltas[0], suspicious_folder)
    copy_remaining_reference_values(refrnce_set, trimmed_filename, main_folder, suspicious_folder)

    return {suspicious_folder.name: refrnce_set}

def make_nearest_values_tuple(target_value: str, list_to_search: List[Tuple[str, ...]]) -> Tuple[str, ...]:
    """
    Gets the value of interest/suspicious file and finds the three nearest values.

    Args:
        target_value (str): Flagged filename.
        list_to_search (List[Tuple[str, ...]]): List with deltas and filenames.

    Returns:
        Tuple[str, ...]: Tuple containing the flagged filename and its surrounding filenames.
    """
    for idx, each_value in enumerate(list_to_search):
        if target_value[0] == each_value[0]:
            if 2 < idx < len(list_to_search) - 3:
                return tuple(v[0] for v in list_to_search[idx-3:idx+4])
    return ()



def remove_outliers_from_array(data: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Remove outliers from the input array using different methods.

    Args:
        data (np.ndarray): Input array of data points.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: Cleaned arrays using mean, median, and IQR methods.
    """
    mean = np.mean(data)
    std = np.std(data)
    mean_clean = data[(data > mean - 2 * std) & (data < mean + 2 * std)]

    median = np.median(data)
    mad = np.median(np.abs(data - median))
    med_clean = data[(data > median - 2 * mad) & (data < median + 2 * mad)]

    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    iqr_clean = data[(data > q1 - 1.5 * iqr) & (data < q3 + 1.5 * iqr)]

    return mean_clean, med_clean, iqr_clean

def get_kmeans_clusters(cleaned_array: np.ndarray, base_path: Path, n: int) -> None:
    """
    Perform K-means clustering on the cleaned array.

    Args:
        cleaned_array (np.ndarray): Array of cleaned data points.
        base_path (Path): Base path for saving results.
        n (int): Iteration number.
    """
    kmeans = KMeans(n_clusters=2, random_state=0).fit(cleaned_array.reshape(-1, 1))
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    output_file = base_path / f"kmeans_results_{n}.txt"
    with output_file.open("w") as f:
        f.write(f"Centroids: {centroids}\n")
        f.write(f"Labels: {labels}\n")

def filtered_duplicates_mask(retrieve_id_mask: callable, tuple_dups: List[Tuple]) -> List[Tuple]:
    """
    Filter duplicates based on a mask.

    Args:
        retrieve_id_mask (callable): Function to retrieve ID mask.
        tuple_dups (List[Tuple]): List of duplicate tuples.

    Returns:
        List[Tuple]: Filtered list of duplicates.
    """
    rgx_mask = r"S[0-9]{3}F[0-9]{2}"
    return [tup for tup in tuple_dups if retrieve_id_mask(rgx_mask, tup[0])]

def copy_wrong_sidenames(filtered_tuple_dups: List[Tuple], path_to_wrong_side_labels: Path, 
                         base_path: Path, cleaned_again_list: List[Tuple[str, str]]) -> None:
    """
    Copy files with wrong side names to a separate folder.

    Args:
        filtered_tuple_dups (List[Tuple]): Filtered list of duplicates.
        path_to_wrong_side_labels (Path): Path to store wrong side labels.
        base_path (Path): Base path of the study.
        cleaned_again_list (List[Tuple[str, str]]): List of cleaned filenames and timestamps.
    """
    path_to_wrong_side_labels.mkdir(exist_ok=True)
    
    for tup in filtered_tuple_dups:
        subject_id = retrieve_id_mask(r"S[0-9]{3}", tup[0])
        subject_folder = path_to_wrong_side_labels / subject_id
        subject_folder.mkdir(exist_ok=True)
        
        shutil.copy2(base_path / tup[0], subject_folder)
        
        nearest_values = make_nearest_values_tuple(tup, cleaned_again_list)
        for file in nearest_values:
            if file != tup[0]:
                shutil.copy2(base_path / file, subject_folder)

def retrieve_id_mask(mask: str, filename: str) -> Optional[str]:
    """
    Retrieve ID mask from filename.

    Args:
        mask (str): Regular expression mask.
        filename (str): Filename to search for mask.

    Returns:
        Optional[str]: Retrieved ID or None if not found.
    """
    match = re.search(mask, filename)
    return match.group(0) if match else None


def remove_outliers_from_array(data: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Remove outliers from the input array using different methods.

    Args:
        data (np.ndarray): Input array of data points.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: Cleaned arrays using mean, median, and IQR methods.
    """
    mean, std = np.mean(data), np.std(data)
    mean_clean = data[(data > mean - 2 * std) & (data < mean + 2 * std)]

    median = np.median(data)
    mad = np.median(np.abs(data - median))
    med_clean = data[(data > median - 2 * mad) & (data < median + 2 * mad)]

    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    iqr_clean = data[(data > q1 - 1.5 * iqr) & (data < q3 + 1.5 * iqr)]

    return mean_clean, med_clean, iqr_clean

def get_kmeans_clusters(cleaned_array: np.ndarray, base_path: Path, n: int) -> None:
    """
    Perform K-means clustering on the cleaned array and save results.

    Args:
        cleaned_array (np.ndarray): Array of cleaned data points.
        base_path (Path): Base path for saving results.
        n (int): Iteration number.
    """
    kmeans = KMeans(n_clusters=2, random_state=0).fit(cleaned_array.reshape(-1, 1))
    
    output_file = base_path / f"kmeans_results_{n}.txt"
    with output_file.open("w") as f:
        f.write(f"Centroids: {kmeans.cluster_centers_}\n")
        f.write(f"Labels: {kmeans.labels_}\n")

def copy_remaining_reference_values(refrnce_set: Set[str], trimmed_filename: str, main_folder: Path, suspicious_folder: Path) -> None:
    """
    Copy remaining reference values to the suspicious folder.

    Args:
        refrnce_set (Set[str]): Set of reference filenames.
        trimmed_filename (str): Trimmed filename without extension.
        main_folder (Path): Path to the main folder.
        suspicious_folder (Path): Path to the suspicious folder.
    """
    for file in refrnce_set:
        if file != f"{trimmed_filename}.jpg":
            shutil.copy2(main_folder / file, suspicious_folder)

def make_nearest_values_tuple(target_value: str, list_to_search: List[Tuple[str, ...]]) -> Tuple[str, ...]:
    """
    Get the value of interest and find the three nearest values.

    Args:
        target_value (str): Flagged filename.
        list_to_search (List[Tuple[str, ...]]): List with deltas and filenames.

    Returns:
        Tuple[str, ...]: Tuple containing the flagged filename and its surrounding filenames.
    """
    for idx, each_value in enumerate(list_to_search):
        if target_value[0] == each_value[0]:
            if 2 < idx < len(list_to_search) - 3:
                return tuple(v[0] for v in list_to_search[idx-3:idx+4])
    return ()



