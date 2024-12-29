import os
from typing import Dict, List, Tuple
from pathlib import Path

from Common_functions import retrieve_id_mask, get_time_sorted_filelist_from_basepath, find_delta

def read_log_dict(log_path: Path) -> Dict[str, str]:
    """
    Read and evaluate the log dictionary from a file.

    Args:
        log_path (Path): Path to the log file.

    Returns:
        Dict[str, str]: The log dictionary.

    Raises:
        ValueError: If the file content is not a valid dictionary.
    """
    with open(log_path, "r") as file:
        content = file.read().replace("\\n", "")
    log_dict = eval(content)
    if not isinstance(log_dict, dict):
        raise ValueError("Log file does not contain a valid dictionary.")
    return log_dict

def process_file(current_file: str, log_dict: Dict[str, str], path_to_images: Path, delta_list: List[Tuple]) -> None:
    """
    Process a file, updating logs and renaming files if necessary.

    Args:
        current_file (str): The current file being processed.
        log_dict (Dict[str, str]): The log dictionary.
        path_to_images (Path): Path to the image directory.
        delta_list (List[Tuple]): List of delta tuples.
    """
    log_path = path_to_images / "log_duplicate.txt"
    
    if current_file in log_dict:
        with open(log_path, "a") as log:
            print(f"{log_dict[current_file]} converted back to --> {current_file} [SUCCESS]", file=log)
    elif current_file in log_dict.values():
        key_required = next(k for k, v in log_dict.items() if v == current_file)
        with open(log_path, "a") as log:
            print(f"{log_dict[key_required]} converted back to --> {key_required} [FAILED]", file=log)
        
        old = path_to_images / log_dict[key_required]
        new = path_to_images / key_required
        old_raw = path_to_images / log_dict[key_required].replace(".jpg", ".cr2")
        new_raw = path_to_images / key_required.replace(".jpg", ".cr2")
        os.rename(old, new)
        os.rename(old_raw, new_raw)
        
        log_bad_file_details(log_path, log_dict[key_required], delta_list)

def log_bad_file_details(log_path: Path, bad_file: str, delta_list: List[Tuple]) -> None:
    """
    Log details about a bad file.

    Args:
        log_path (Path): Path to the log file.
        bad_file (str): Name of the bad file.
        delta_list (List[Tuple]): List of delta tuples.
    """
    bad_file_entries = [tup for tup in delta_list if bad_file == tup[0]]
    if bad_file_entries:
        idx_val = delta_list.index(bad_file_entries[0])
        relevant_entries = [delta_list[idx_val-1]] + bad_file_entries + [delta_list[idx_val+1]]
        with open(log_path, "a") as log:
            print(f"Details regarding the bad file {bad_file} are as follows: ", file=log)
            for entry in relevant_entries:
                print(f"{entry}", file=log)

def main():
    """
    Main function to process image files and update logs.
    """
    rgx_ending = r"_[0-9]{4}"
    path_to_images = Path(r'Path to image folder')
    log_path = path_to_images / "log_duplicate.txt"

    try:
        log_dict = read_log_dict(log_path)
    except ValueError as e:
        print(f"Error: {e}")
        return

    timepoint_sorted = get_time_sorted_filelist_from_basepath(path_to_images, ".jpg")
    delta_list, _ = find_delta(timepoint_sorted)

    for key in log_dict.keys():
        file_ending = retrieve_id_mask(rgx_ending, key)[1:]
        matching_files = [f for f in os.listdir(path_to_images) if f.endswith("jpg") and file_ending in f]
        
        if len(matching_files) > 1:
            print(f"Error: More than one filename has ending number {file_ending}. Quitting...")
            break
        elif len(matching_files) == 1:
            process_file(matching_files[0], log_dict, path_to_images, delta_list)

if __name__ == '__main__':
    main()
