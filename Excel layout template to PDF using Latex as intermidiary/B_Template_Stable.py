import re
import os
from typing import Dict, Tuple

def return_correct_digit(orig_id: str) -> str:
    """
    Returns the correct subject identifier. If the original ID starts with "0",
    the function returns the last digit of the ID; otherwise, it returns the ID unchanged.

    Args:
        orig_id (str): The original subject ID.

    Returns:
        str: The corrected subject ID.
    """
    if orig_id[0] != "0":
        return orig_id
    else:
        return orig_id[-1]


def do_the_B_transform(fpath: str, beir_rand_fpath: str) -> Tuple[str, str]:
    """
    Modifies the LaTeX page headers in a given file by replacing subject IDs 
    with their corresponding product information from a randomization file.

    Args:
        fpath (str): The file path to the LaTeX file to be modified.
        beir_rand_fpath (str): The file path to the randomization file containing
                               subject ID-to-product mappings.

    Returns:
        Tuple[str, str]: A tuple containing:
                         - The base name of the new LaTeX file.
                         - The full path to the new LaTeX file.
    """
    # Regular expression to extract subject IDs (e.g., "Subject 1", "Subject 23")
    Id_mask = re.compile(r"Subject [0-9]*")
    rand_dict: Dict[str, str] = {}

    # Parse the randomization file into a dictionary
    with open(beir_rand_fpath, encoding='utf-8') as frand:
        rand_gen = iter(frand.readlines())
    
    while True:
        try:
            l = next(rand_gen)
            rand_dict[l.split("\t")[0].replace("ï»¿", "")] = l.split("\t")[1]  # Remove BOM character if present
        except StopIteration:
            break
    print(rand_dict)

    # Read the LaTeX file and transform the subject IDs
    with open(fpath, encoding='utf-8') as ftex:
        lines_gen = iter(ftex.readlines())
    
    tex_temp = []
    while True:
        try:
            l = next(lines_gen)
            if "Subject" in l:
                l_interest = l
                # Extract the subject ID
                Subj_id = Id_mask.search(l).group(0)
                print(Subj_id[-2:])
                dict_returned = rand_dict[return_correct_digit(Subj_id[-2:])].replace("\n", "")

                # Map randomization number to product description
                if dict_returned == "30":
                    Prod = "Cleansner A + Fluid A(morning) + Fluid A(evening)"
                elif dict_returned == "20":
                    Prod = "Cleansner B + Fluid B(morning) + Fluid B(evening)"
                else:
                    Prod = "Unknown Product"
                
                # Modify the LaTeX line to include the product description
                l_mod = l_interest.replace(f"{Subj_id}", f"{Subj_id} ({Prod})")
                tex_temp.append(l_mod)
            else:
                tex_temp.append(l)
        except StopIteration:
            break

    # Write the modified LaTeX content to a new file
    new_file_name = fpath.split("\\")[-1][:-4]
    new_file_path = os.path.join(os.getcwd(), f"{new_file_name}_appended.tex")
    with open(new_file_path, "w", encoding='utf-8') as f_new:
        for line in tex_temp:
            f_new.write(line)

    return new_file_name, new_file_path
