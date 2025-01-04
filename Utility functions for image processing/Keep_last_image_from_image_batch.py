"""
This script processes images in a specified directory, checks their filenames against a predefined regex pattern, 
and separates them into two categories:
1. **Superseeded files**: Older or redundant files based on the regex-sorted criteria are moved to a specific folder.
2. **Correctly named files**: Files with valid and desired naming conventions.

Key functionalities:
1. Uses regex to parse filenames and extract metadata (e.g., subject ID, area, visit, image number).
2. Moves improperly named or redundant files to designated directories.
3. Logs operations for debugging and record-keeping.
"""


import os
import inspect
import logging
import re
import Util
import shutil
from typing import List, Optional

# Paths and Directories
rawPath = r"path_to_images"
outputPath = os.path.join(rawPath, "superseeded_auto")
outputPathWrongName = os.path.join(rawPath, "wrong_name_auto")

# Logger Configuration
loggerName = os.path.splitext(os.path.basename(inspect.getfile(inspect.currentframe())))[0]
logger = Util.createStandardLogger(loggerName, os.path.join(outputPath, f"{loggerName}.log"))
logger.setLevel(logging.DEBUG)

# Regex Pattern
FILE_STUDYNM_END = "FTO240286"
REGEX_PTRN = (
    r"^S(?P<subj_int>[0-9]{3})F(?P<area_int>[0-9]{2})T(?P<visit_int>[0-9]{2})"
    + FILE_STUDYNM_END
    + r"_(?P<imnr_int>[0-9]{4})"
)

# Indices for extracted metadata
study_subjInd = 0
study_areaInd = 1
study_timeInd = 2
study_restNameInd = 3

def getDataFromBasefile(filename: str, fullfile: str) -> Optional[List]:
    """
    Extracts metadata from a filename using a regex pattern.

    :param filename: Base name of the file (without path).
    :param fullfile: Full file path.
    :return: List of extracted metadata [subject ID, area, visit, image number, filename, fullfile], or None if regex doesn't match.
    """
    fileformat = re.compile(REGEX_PTRN)
    match = fileformat.search(filename)
    if match is None:
        return None
    return [
        int(match.group("subj_int")),
        int(match.group("area_int")),
        int(match.group("visit_int")),
        int(match.group("imnr_int")),
        filename,
        fullfile,
    ]


def process_files(raw_path: str, output_path: str, output_path_wrong: str, extensions: List[str]) -> None:
    """
    Processes files in the specified directory, separating superseeded and incorrectly named files.

    :param raw_path: Path containing the raw files.
    :param output_path: Directory to move superseeded files.
    :param output_path_wrong: Directory to move incorrectly named files.
    :param extensions: List of file extensions to process.
    """
    Util.createDirectory(output_path_wrong)

    # Gather all files matching the given extensions
    for extn in extensions:
        filenames = Util.getAllFiles(raw_path, extn, depth=0)

        # Check file naming validity
        Util.check_study_data_with_err_data(
            raw_path,
            extn,
            REGEX_PTRN,
            ["subj_int", "area_int", "visit_int", "imnr_int"],
            -1,
            search_depth=0,
            wait_input=True,
            do_test=True,
            key_remove_list=[3],
        )

        # Extract metadata and filter valid/invalid files
        file_data = list(map(lambda file: getDataFromBasefile(os.path.basename(file), file), filenames))
        for filename, data in zip(filenames, file_data):
            if data is None:
                shutil.move(filename, output_path_wrong)
        file_data = list(filter(lambda x: x is not None, file_data))

        # Process files into superseeded and keep lists
        superseeded_files = []
        keep_files = []
        volumes = set(x[study_subjInd] for x in file_data)
        areas = set(x[study_areaInd] for x in file_data)
        time_list = set(x[study_timeInd] for x in file_data)

        for vol in volumes:
            for area in areas:
                for time in time_list:
                    relevant_data = [
                        x
                        for x in file_data
                        if x[study_subjInd] == vol
                        and x[study_areaInd] == area
                        and x[study_timeInd] == time
                    ]
                    if len(relevant_data) > 1:
                        relevant_data.sort(key=lambda x: x[study_restNameInd])
                        superseeded_files.extend([x[-1] for x in relevant_data[:-1]])
                    elif relevant_data:
                        keep_files.append(relevant_data[-1][-1])

        # Move superseeded files to the output directory
        Util.createDirectory(output_path)
        for file in superseeded_files:
            shutil.move(file, output_path)

        logger.info(f"Superseeded files moved: {len(superseeded_files)}")
        logger.info(f"Files kept: {len(keep_files)}")


if __name__ == "__main__":
    # Extensions to process
    extensions_to_check = ["S*.jpg", "S*.cr2"]

    # Run the processing
    process_files(rawPath, outputPath, outputPathWrongName, extensions_to_check)
