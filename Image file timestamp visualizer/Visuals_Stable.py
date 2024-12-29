import datetime
import exifread
import os
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import itertools
import sys
from pathlib import Path
from typing import List, Tuple, Dict

def vis_data_and_display(file_sorted_list: List[Tuple[str, str]], 
                         Base_path: Path, 
                         saved_filecount: int, 
                         f_ext: str) -> Tuple[int, List[Tuple[str, str]]]:
    """
    Visualizes and displays data, filtering images by time delta and subject changes.

    Args:
        file_sorted_list (List[Tuple[str, str]]): Sorted list of image filenames and their EXIF timestamps.
        Base_path (Path): Base path for the image files.
        saved_filecount (int): Counter for saved files.
        f_ext (str): File extension to filter images (e.g., '.jpg').

    Returns:
        Tuple[int, List[Tuple[str, str]]]: Updated saved file count and the sorted list of files.
    """
    file_list = [
        (entry.name, get_original_time_from_exif(entry.name, Base_path))
        for entry in Base_path.iterdir() if entry.is_file() and entry.suffix == f_ext
    ]
    
    file_sorted_list = sorted(file_list, key=lambda x: x[1])
    delta_list = find_delta(file_sorted_list)

    filtered_values_thresholded = [
        (deltaa[0], deltaa[-1]) for n, deltaa in enumerate(delta_list) if n == 0 or deltaa[-1] > 2 * 60
    ]

    cleaned_filtered_values_thresholded = []
    box_plot_list = []  # For later visualization step

    subj_name_temp_check = None
    for n, flagged_delta in enumerate(filtered_values_thresholded):
        if n == 0:  # Get first subject ID
            subj_name_temp_check = flagged_delta[0][:4]
            cleaned_filtered_values_thresholded.append(flagged_delta)
        elif flagged_delta[0][:4] != subj_name_temp_check:
            cleaned_filtered_values_thresholded.append(flagged_delta)
        elif flagged_delta[0][:4] == subj_name_temp_check:
            all_files_more_than_2min = list(filter(lambda x: subj_name_temp_check in x[0], delta_list))
            box_plot_list.append(all_files_more_than_2min)

    saved_filecount = stats_and_visualization(delta_list, file_sorted_list, cleaned_filtered_values_thresholded,
                                              filtered_values_thresholded, Base_path, saved_filecount)
    return saved_filecount, file_sorted_list

def get_original_time_from_exif(filename: str, basepath: Path) -> str:
    """
    Retrieves the original timestamp from the EXIF metadata of an image.

    Args:
        filename (str): Name of the image file.
        basepath (Path): Path to the directory containing the image.

    Returns:
        str: The original timestamp in 'YYYY:MM:DD HH:MM:SS' format.
    """
    abs_path_to_image = basepath / filename
    with open(abs_path_to_image, 'rb') as f:
        tags = exifread.process_file(f)

    date = tags.get('Image DateTime')
    if date:
        return str(date)
    else:
        print("Date is still None. Exiting.")
        sys.exit()

def retrieve_timestamp_of_filename_provided(filename: str, lookup_list: List[Tuple[str, str]]) -> str:
    """
    Retrieves the timestamp for a given filename from a lookup list.

    Args:
        filename (str): Name of the image file.
        lookup_list (List[Tuple[str, str]]): List of filenames and their corresponding timestamps.

    Returns:
        str: The timestamp associated with the filename.
    """
    for item in lookup_list:
        if filename in item:
            return item[-1]

def find_delta(original_list_with_times: List[Tuple[str, str]]) -> List[Tuple[str, str, str, str, int]]:
    """
    Computes the time differences (delta) between consecutive image timestamps.

    Args:
        original_list_with_times (List[Tuple[str, str]]): List of image filenames and their corresponding timestamps.

    Returns:
        List[Tuple[str, str, str, str, int]]: List of deltas between consecutive image timestamps.
    """
    list_with_deltas = []
    for i in range(1, len(original_list_with_times)):
        previous_file, previous_val = original_list_with_times[i - 1]
        current_file, current_val = original_list_with_times[i]
        delta = datetime.datetime.strptime(current_val, '%Y:%m:%d %H:%M:%S') - datetime.datetime.strptime(previous_val, '%Y:%m:%d %H:%M:%S')
        list_with_deltas.append((previous_file, current_file, str(previous_val), str(current_val), delta.seconds))
    return list_with_deltas

def stats_and_visualization(delta_list: List[Tuple[str, str, str, str, int]], 
                            file_list_sorted: List[Tuple[str, str]], 
                            cleaned_filtered_values_thresholded: List[Tuple[str, int]], 
                            filtered_values_thresholded: List[Tuple[str, int]], 
                            base_path_name: Path, 
                            saved_counts: int) -> int:
    """
    Generates statistics and visualizations based on the time deltas between image captures.

    Args:
        delta_list (List[Tuple[str, str, str, str, int]]): List of deltas between consecutive image timestamps.
        file_list_sorted (List[Tuple[str, str]]): Sorted list of image filenames and their timestamps.
        cleaned_filtered_values_thresholded (List[Tuple[str, int]]): Cleaned list of thresholded values based on subject changes.
        filtered_values_thresholded (List[Tuple[str, int]]): List of thresholded values based on time deltas.
        base_path_name (Path): Base path for saving the visualization.
        saved_counts (int): Counter for saved files.

    Returns:
        int: Updated count of saved files.
    """
    difference_between_subject_changes = [(sub_change[0], retrieve_timestamp_of_filename_provided(sub_change[0], file_list_sorted)) 
                                          for sub_change in cleaned_filtered_values_thresholded]
    deltas_between_subject_changes = find_delta(difference_between_subject_changes)

    subj_deltas_only = [delta[-1] for delta in deltas_between_subject_changes]
    print(f"The mean of subject deltas is: {np.mean(subj_deltas_only)} seconds ({np.mean(subj_deltas_only)/60} minutes)")

    pd.plotting.register_matplotlib_converters()

    data_set_VOI = pd.DataFrame([d[-1] for d in delta_list], index=[d[0] for d in delta_list])
    data_set_VOIclean = pd.DataFrame([d[-1] for d in filtered_values_thresholded], index=[d[0] for d in filtered_values_thresholded])
    data_set_VOIclean_subj_only = pd.DataFrame([d[-1] for d in cleaned_filtered_values_thresholded], index=[d[0] for d in cleaned_filtered_values_thresholded])
    data_set_subj_diff = pd.DataFrame([d[-1] for d in deltas_between_subject_changes], index=[d[0] for d in deltas_between_subject_changes])

    _, axs = plt.subplots(4, 1, figsize=(3, 9))
    axs[0].plot(data_set_VOI, color='red', marker='o', markersize=0.9,  linewidth=0.3, linestyle='dashed')
    axs[0].set_title("Original data includes all deltas and filenames")
    axs[1].plot(data_set_VOIclean, color='blue', marker='o', markersize=0.9, linewidth=0.3, linestyle='dashed')
    axs[1].set_title("Deltas > 2")
    axs[2].plot(data_set_VOIclean_subj_only, color='green', marker='o', markersize=0.9, linewidth=0.3, linestyle='dashed')
    axs[2].set_title("Only subject changes, no duplicates")
    axs[3].plot(data_set_subj_diff, color='magenta', marker='o', markersize=0.9, linewidth=0.3, linestyle='dashed')
    axs[3].set_title("Subject change deltas")

    mplcursors.cursor()
    plt.savefig(base_path_name / f"Figure_{saved_counts}.eps", format='eps', bbox_inches='tight')
    plt.tight_layout()
    plt.show()
    saved_counts += 1
    return saved_counts

def visualize_timestamp_per_folder(base_path: Path) -> None:
    """
    Visualizes timestamps of images in each folder.

    Args:
        base_path (Path): Path to the base directory containing folders with images.
    """
    plot_dict: Dict[str, List[Tuple[str, datetime.datetime]]] = {}

    for foldr in os.listdir(base_path):
        plot_list = []
        for file_n in os.listdir(base_path / foldr):
            time_stamp = datetime.datetime.strptime(get_original_time_from_exif(file_n, base_path / foldr), '%Y:%m:%d %H:%M:%S')
            plot_list.append((file_n, time_stamp))
        plot_dict[foldr] = sorted(plot_list, key=lambda x: x[-1])

    if len(plot_dict) == 1:
        for plt_key in plot_dict.keys():
            plt.plot([f[0] for f in plot_dict[plt_key]], [f[-1] for f in plot_dict[plt_key]], marker='o', markersize=0.9, linewidth=0.3, linestyle='dashed')
            plt.title(plt_key)
            break
    elif len(plot_dict) > 1:
        _, axs = plt.subplots(len(plot_dict), 1, figsize=(3, 9))
        for n, plt_key in enumerate(plot_dict.keys()):
            axs[n].plot([f[0] for f in plot_dict[plt_key]], [f[-1] for f in plot_dict[plt_key]], marker='o', markersize=0.9, linewidth=0.3, linestyle='dashed')
            axs[n].set_title(plt_key)
    else:
        print("No plots can be generated from an empty folder")

    mplcursors.cursor()
    plt.tight_layout()
    plt.show()
