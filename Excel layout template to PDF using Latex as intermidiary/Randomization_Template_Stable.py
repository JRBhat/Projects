import Common_Functions_Stable as CFS
import re
from typing import List, Tuple, Iterator

def randomize_custom_rand_alllightingcode(
    filelist: List[str],
    randomfilepath: str,
    area_id_list: List[str],
    time_id_list: List[str],
    sorted_subject_id_list: List[str]
) -> Iterator[Tuple[str, str]]:
    """
    Randomizes a list of file paths by associating them with randomized light codes, subject IDs, area IDs, and time IDs.
    
    Args:
        filelist (List[str]): List of file paths to be randomized.
        randomfilepath (str): Path to the randomization file.
        area_id_list (List[str]): List of area IDs to consider.
        time_id_list (List[str]): List of time IDs to consider.
        sorted_subject_id_list (List[str]): List of sorted subject IDs.

    Returns:
        Iterator[Tuple[str, str]]: An iterator of tuples, where each tuple contains a file path and a corresponding random code.
    """
    # create tuple (filepath, (subid, *areaid/timeid)) # *needs to be changed depending on template requirement
    tuple_list_with_path_and_ids = []

    # e.g. clone random sequence for each light code in visia 
    light_id_list = []
    for filepath in filelist:
        filenm = filepath.split("\\")[-1]
        light_code = re.search(r"S[0-9]{3}F[0-9]{2}T[0-9]{2}([0-9A-Za-z]{4})", filenm).group(1)
        light_id_list.append(light_code)
        
    light_id_list = list(set(light_id_list))
    for subj in sorted_subject_id_list:
        for time in time_id_list:
            for ar in area_id_list:
                for li in light_id_list:
                    for filepath in filelist:
                        filenm = filepath.split("\\")[-1]
                        if subj in filenm and ar in filenm and time in filenm and li in filenm:
                            tuple_list_with_path_and_ids.append((filepath, (subj, ar, time, li)))

    print(tuple_list_with_path_and_ids)

    # read random sequence from the randomization file (.txt file in study folder) and validate subject ids (check if file has equal number of subjects)
    cleaned_list = CFS.validate_random_file(randomfilepath, sorted_subject_id_list)
    print(cleaned_list)

    # create a dictionary with tuple (sub, arid) as key and value as Product alphabet from line per subject 
    mapping_dict = {}
    for line, subj in zip(cleaned_list, sorted_subject_id_list):
        for p_id, ar in zip(line, area_id_list):
            for time in time_id_list:
                for li in light_id_list:
                   mapping_dict[(subj, ar, time, li)] = p_id        
    
    print(mapping_dict)

    # map each tuple in tuple_list_with_ids with ids(values) using mapping_dict's keys
    derandomized_list = []
    for subj in sorted_subject_id_list:
        grouped_by_subj = [(tupl[0], mapping_dict[tupl[1]]) for tupl in tuple_list_with_path_and_ids if subj == tupl[1][0]]
        derandomized_paths_grouped_per_subj = sorted(grouped_by_subj, key=lambda x: x[1])
        derandomized_list.append(derandomized_paths_grouped_per_subj)
    
    final_derandomized_list = []
    for sub_list in derandomized_list:
        for tup in sub_list:
            final_derandomized_list.append(tup)

    print(final_derandomized_list)

    final_randomised_list_iter = iter(final_derandomized_list)
    return final_randomised_list_iter


def randomize_std(
    filelist: List[str],
    randomfilepath: str,
    area_id_list: List[str],
    time_id_list: List[str],
    sorted_subject_id_list: List[str]
) -> Iterator[Tuple[str, str]]:
    """
    Randomizes a list of file paths by associating them with subject IDs, area IDs, and time IDs, using a standard template.
    
    Args:
        filelist (List[str]): List of file paths to be randomized.
        randomfilepath (str): Path to the randomization file.
        area_id_list (List[str]): List of area IDs to consider.
        time_id_list (List[str]): List of time IDs to consider.
        sorted_subject_id_list (List[str]): List of sorted subject IDs.

    Returns:
        Iterator[Tuple[str, str]]: An iterator of tuples, where each tuple contains a file path and a corresponding random code.
    """
    tuple_list_with_path_and_ids = []

    for subj in sorted_subject_id_list:
        for ar in area_id_list:
            for tim in time_id_list:
                for filepath in filelist:
                    filenm = filepath.split("\\")[-1]
                    if subj in filenm and ar in filenm and tim in filenm:
                        # validation
                        val_code = CFS.extract_elements_from_regex_mask(filenm, r"S[0-9]{3}F[0-9]{2}")
                        comparison = str(subj + ar)
                        if val_code == comparison:
                            tuple_list_with_path_and_ids.append((filepath, (subj, ar)))
                        else:
                            print(f"val id in path({val_code}) does not match with comparison iterator ({comparison})")
                            raise BaseException

    print(tuple_list_with_path_and_ids)

    # read random sequence from the randomization file (.txt file in study folder) and validate subject ids (check if file has equal number of subjects)
    cleaned_list = CFS.validate_random_file(randomfilepath, sorted_subject_id_list)
    print(cleaned_list)

    # create a dictionary with tuple (sub, arid) as key and value as Product alphabet from line per subject 
    mapping_dict = {}
    for line, subj in zip(cleaned_list, sorted_subject_id_list):
        for p_id, ar in zip(line, area_id_list):
            mapping_dict[(subj, ar)] = p_id        

    print(mapping_dict)

    # map each tuple in tuple_list_with_ids with ids(values) using mapping_dict's keys
    derandomized_list = []
    for subj in sorted_subject_id_list:
        grouped_by_subj = [(tupl[0], mapping_dict[tupl[1]]) for tupl in tuple_list_with_path_and_ids if subj == tupl[1][0]]
        derandomized_paths_grouped_per_subj = sorted(grouped_by_subj, key=lambda x: x[1])
        derandomized_list.append(derandomized_paths_grouped_per_subj)
    
    final_derandomized_list = []
    for sub_list in derandomized_list:
        for tup in sub_list:
            final_derandomized_list.append(tup)

    print(final_derandomized_list)

    final_randomised_list_iter = iter(final_derandomized_list)
    return final_randomised_list_iter
