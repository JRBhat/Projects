"""
This script organizes and renames image files in a specified directory by grouping them based on subject, 
area, and timepoint extracted from their filenames. It then renames the files in a sequential order for each group.
"""

import os
import re
from typing import List, Dict, Tuple
from Util import getAllFiles

# Path to the directory containing the files and the file extension mask
PATH: str = r"path_to_images"
MASK: str = r"*.TIF"

def main() -> None:
    """
    Processes files in the specified directory by:
    - Extracting subject, area, and timepoint data using a regular expression.
    - Grouping the files into a dictionary based on the extracted data.
    - Sorting and renaming files in sequential order for each group.

    The script renames files in place and prints the renaming operations.
    """
    # Lists to store extracted data
    subjects_list: List[str] = []
    areas_list: List[str] = []
    timepoints_list: List[str] = []
    
    # Regular expression pattern to parse filenames
    regmask: str = r"(S[0-9]{3})(F[0-9]{2})(T[0-9]{2})ABC999999_([0-9]*)"
    files: List[str] = getAllFiles(PATH, MASK)
    
    # Extract subject, area, and timepoint data from filenames
    for fpath in files:
        fname: str = fpath.split("\\")[-1]
        subjects_list.append(re.search(regmask, fname).group(1))
        areas_list.append(re.search(regmask, fname).group(2))
        timepoints_list.append(re.search(regmask, fname).group(3))
        
    # Create sets to group unique subjects, areas, and timepoints
    subjs: set = set(subjects_list)
    areas: set = set(areas_list)
    times: set = set(timepoints_list)
        
    # Initialize a dictionary to group files by subject, area, and timepoint
    mega_dict: Dict[Tuple[str, str, str], List[str]] = {(s, a, t): [] for s in subjs for a in areas for t in times}
   
    # Populate the dictionary with filenames grouped by subject, area, and timepoint
    for fn in os.listdir(PATH):
        match = re.search(regmask, fn)
        if match:
            s, a, t = match.group(1), match.group(2), match.group(3)
            mega_dict[(s, a, t)].append(fn)
    
    # Create a sorted copy of the dictionary based on the sequence number in filenames
    mega_dict2: Dict[Tuple[str, str, str], List[str]] = mega_dict.copy()
    for k in mega_dict.keys():
        sorted_fn_list: List[str] = sorted(mega_dict[k], key=lambda x: re.search(regmask, x).group(4))
        mega_dict2[k] = sorted_fn_list
        
    # Create a final dictionary where files are paired with their new names
    mega_dict3: Dict[Tuple[str, str, str], List[Tuple[str, str]]] = mega_dict2.copy()
    for k in mega_dict2.keys():
        count: int = 1
        for idx, item in enumerate(mega_dict2[k]):
            if count == 1:
                mega_dict3[k][idx] = (item, item)
            else:
                mega_dict3[k][idx] = (item, item.replace("F01", f"F0{count}"))
            count += 1

    # Rename the files based on the final dictionary
    for v in mega_dict3.values():
        for item in v:
            old_fpath: str = os.path.join(PATH, item[0])
            new_fpath: str = os.path.join(PATH, item[1])
            os.rename(old_fpath, new_fpath)
            print(f"{item[0]} ---> {item[1]}")
            
if __name__ == "__main__":
    main()
