import os
import random
from typing import List, Dict, Tuple
from pathlib import Path

from Common_functions import retrieve_id_mask

# Constants
UNIVERSAL_REGEX = r"S[0-9]{3}F[0-9]{2}T[0-9]{2}[_0-9A-Za-z]*_[0-9]*"
SUBJECT_ID_REGEX = r"S[0-9]{3}"
SIDE_ID_REGEX = r"F[0-9]{2}"
IMAGE_INDEX_REGEX = r"_[0-9]*"

PATH_TO_IMAGES = Path(r'Path to image folder')
CHANGED_SIDE_NAMES = 1
CHANGED_SUBJECT_NAMES = 1

def get_image_files(path: Path) -> List[str]:
    """Return a list of all JPG files in the given directory."""
    return [f for f in os.listdir(path) if f.endswith("jpg")]

def get_unique_sorted_ids(id_list: List[str]) -> List[str]:
    """Return a sorted list of unique IDs."""
    return sorted(set(id_list), key=lambda x: int(x[-2:]))

def get_subject_and_side_ids(file_list: List[str]) -> Tuple[List[str], List[str]]:
    """Extract subject and side IDs from file names."""
    subject_ids = [retrieve_id_mask(SUBJECT_ID_REGEX, fn) for fn in file_list]
    side_ids = [retrieve_id_mask(SIDE_ID_REGEX, fn) for fn in file_list]
    return get_unique_sorted_ids(subject_ids)[:-1], get_unique_sorted_ids(side_ids)

def group_images_by_subject(file_list: List[str], subject_ids: List[str]) -> List[List[str]]:
    """Group images by subject ID."""
    return [[x for x in file_list if subj in x] for subj in subject_ids]

def change_side_names(file_list: List[str], subject_ids: List[str], side_ids: List[str], 
                      num_changes: int) -> Dict[str, str]:
    """Change side names for a specified number of files."""
    change_log = {}
    ignore_subjects = []

    for _ in range(num_changes):
        rand_subj = random.choice([s for s in subject_ids if s not in ignore_subjects])
        rand_side = random.choice(side_ids)
        ignore_subjects.append(rand_subj)

        matching_files = [f for f in file_list if rand_subj in f and rand_side in f]
        if not matching_files:
            continue

        file_to_change = max(matching_files, key=lambda x: int(retrieve_id_mask(IMAGE_INDEX_REGEX, x)[1:]))
        current_side = retrieve_id_mask(SIDE_ID_REGEX, file_to_change)
        new_side = side_ids[(side_ids.index(current_side) + 1) % len(side_ids)]
        
        new_filename = file_to_change.replace(current_side, new_side)
        change_log[file_to_change] = new_filename

    return change_log

def change_subject_names(file_list: List[str], subject_ids: List[str], side_ids: List[str], 
                         num_changes: int, ignore_subjects: List[str]) -> Dict[str, str]:
    """Change subject names for a specified number of files."""
    change_log = {}

    for _ in range(num_changes):
        rand_subj = random.choice([s for s in subject_ids if s not in ignore_subjects])
        rand_side = random.choice(side_ids)
        ignore_subjects.append(rand_subj)

        matching_files = [f for f in file_list if rand_subj in f and rand_side in f]
        if not matching_files:
            continue

        file_to_change = max(matching_files, key=lambda x: int(retrieve_id_mask(IMAGE_INDEX_REGEX, x)[1:]))
        current_subj = retrieve_id_mask(SUBJECT_ID_REGEX, file_to_change)
        new_subj = subject_ids[(subject_ids.index(current_subj) + 1) % len(subject_ids)]
        
        new_filename = file_to_change.replace(current_subj, new_subj)
        change_log[file_to_change] = new_filename

    return change_log

def rename_files(change_log: Dict[str, str], path: Path):
    """Rename files based on the change log."""
    for old_name, new_name in change_log.items():
        old_path = path / old_name
        new_path = path / new_name
        old_path.rename(new_path)
        
        old_raw = old_path.with_suffix('.cr2')
        new_raw = new_path.with_suffix('.cr2')
        if old_raw.exists():
            old_raw.rename(new_raw)

def main():
    file_list = get_image_files(PATH_TO_IMAGES)
    subject_ids, side_ids = get_subject_and_side_ids(file_list)

    if (CHANGED_SIDE_NAMES + CHANGED_SUBJECT_NAMES) >= (len(subject_ids) + len(side_ids)):
        raise ValueError("The required filename changes are more than the ranges of subjects and sides")

    change_log = change_side_names(file_list, subject_ids, side_ids, CHANGED_SIDE_NAMES)
    change_log.update(change_subject_names(file_list, subject_ids, side_ids, CHANGED_SUBJECT_NAMES, 
                                           list(set(f[:4] for f in change_log.keys()))))

    log_path = PATH_TO_IMAGES / "log_duplicate.txt"
    with open(log_path, "w") as log:
        print(change_log, file=log)

    rename_files(change_log, PATH_TO_IMAGES)

if __name__ == "__main__":
    main()
