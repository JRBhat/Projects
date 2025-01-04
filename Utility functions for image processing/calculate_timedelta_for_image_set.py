"""
This script processes image files by extracting timestamps from EXIF metadata or file properties 
and generating a time-sorted list of files. It calculates the time difference between consecutive 
files and writes this data to a CSV file for further analysis.

Key functionalities:
1. Extracts timestamps from images (EXIF, creation, or modification times).
2. Sorts images based on extracted timestamps.
3. Computes time deltas between consecutive images and outputs the results to a CSV file.
"""



import numpy as np
import os
import time
import cv2
import sys
import exifread
from pathlib import Path
import datetime
from typing import List, Tuple
from Util import check_study_data


def get_original_time_from_exif(abs_path_to_image: str, TimeType: str = "Exif") -> str:
    """
    Retrieve the original timestamp of when an image was taken based on metadata or file properties.

    :param abs_path_to_image: Absolute path to the image file.
    :param TimeType: The type of timestamp to retrieve ('Exif', 'C' for creation time, or 'M' for modification time).
    :return: Timestamp in the format 'YYYY:MM:DD HH:MM:SS'.
    :raises SystemExit: If the timestamp cannot be retrieved.
    """
    timestamp: str = None

    if TimeType == "C":
        timestamp = datetime.datetime.strptime(
            time.ctime(os.path.getctime(abs_path_to_image)),
            '%a %b %d %H:%M:%S %Y'
        ).strftime('%Y:%m:%d %H:%M:%S')

    elif TimeType == "M":
        timestamp = datetime.datetime.strptime(
            time.ctime(os.path.getmtime(abs_path_to_image)),
            '%a %b %d %H:%M:%S %Y'
        ).strftime('%Y:%m:%d %H:%M:%S')

    elif TimeType == "Exif":
        with open(abs_path_to_image, 'rb') as f:
            tags = exifread.process_file(f)
        for tag in tags.keys():
            if tag == 'Image DateTime':
                timestamp = str(tags[tag])
                break

    if timestamp is not None:
        return timestamp
    else:
        filename = os.path.basename(abs_path_to_image)
        print(f"Time not found in {filename}. Exiting.")
        sys.exit()


def get_time_sorted_filelist_from_basepath(
    grp_with_paths: List[Tuple[str, str, str, str]],
    file_ext: str,
    timefilter: str
) -> List[Tuple[str, str, str, str, str]]:
    """
    Get a list of filenames and timestamps, sorted by time.

    :param grp_with_paths: List of tuples containing group information and file paths.
    :param file_ext: File extension to filter (e.g., '.jpg').
    :param timefilter: Type of timestamp to use ('Exif', 'C', or 'M').
    :return: Time-sorted list of tuples with filenames and timestamps.
    """
    file_list: List[Tuple[str, str, str, str, str]] = []
    for entry_data in grp_with_paths:
        entry_path = Path(entry_data[-1])
        if entry_path.is_file() and entry_path.suffix == file_ext:
            timestamp = get_original_time_from_exif(entry_path.as_posix(), TimeType=timefilter)
            file_list.append((*entry_data[:-1], entry_path.name, timestamp))

    # Sort the files based on their timestamps
    file_list_sorted = sorted(file_list, key=lambda x: x[-1])
    return file_list_sorted


def main():
    """
    Main function to process image files:
    1. Extracts timestamps from image files.
    2. Sorts the files based on the timestamps.
    3. Computes the time deltas between consecutive files.
    4. Writes the results to a CSV file.
    """
    BASEPATH = r"path_to_images"
    TIME_FILTER = "Exif"  # Options: 'Exif', 'C', 'M'
    EXTN = "*.cr2"

    InputFileParseMask = "S(?P<subj_int>[0-9]*)F(?P<side_int>[0-9]{2})T(?P<time_int>[0-9]{2})"
    InputFileParameters = ["subj_int", "side_int", "time_int"]

    study_data = check_study_data(
        BASEPATH,
        EXTN,
        InputFileParseMask,
        InputFileParameters,
        1,
        search_depth=0,
        key_remove_list=[]
    )
    sorted_grp = get_time_sorted_filelist_from_basepath(study_data, EXTN.replace("*", ""), TIME_FILTER)

    sorted_grp_delta = []
    for idx, entry in enumerate(sorted_grp):
        if idx == 0:
            start_time = datetime.datetime.strptime(entry[-1], '%Y:%m:%d %H:%M:%S')
            sorted_grp_delta.append((*entry, 0))
            continue

        current_time = datetime.datetime.strptime(entry[-1], '%Y:%m:%d %H:%M:%S')
        delta = (current_time - start_time).seconds
        sorted_grp_delta.append((*entry, delta))
        start_time = current_time

    with open("delta_full.csv", "a+") as fl:
        for entry in sorted_grp_delta:
            entry_str = tuple(str(e) for e in entry)
            print("\t".join(entry_str), file=fl)


if __name__ == "__main__":
    main()
