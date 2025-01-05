import re
import os
from typing import List, Tuple, Iterator

# Dictionary with keys (A-G) and Values (Side names)
side_name_dict: dict[str, str] = {
    "A": "Left Upper arm",
    "B": "Right Upper arm",
    "C": "Left Thigh",
    "D": "Right Thigh",
    "E": "Left Calf",
    "F": "Right Calf",
    "G": "Kneecap"
}

def process_randomized_sidenames(randomList_path: str, latest_tex_file_path: str) -> None:
    """
    Processes a randomized list of side names, replacing side names in a LaTeX file with the corresponding side names 
    from the dictionary and creates a new LaTeX file with the updated names.
    
    Args:
        randomList_path (str): Path to the text file containing the randomized list of side identifiers.
        latest_tex_file_path (str): Path to the LaTeX file to be modified.

    Returns:
        None
    """
    
    # Read the random list and replace each character(key) with corresponding dict value
    with open(randomList_path) as randPath:
        lines_randgen: Iterator[str] = iter(randPath.readlines())

    lines_rand: List[str] = []
    while True:
        try:
            lines_rand.append(next(lines_randgen).replace("\n", ""))
        except StopIteration:
            break

    list_rand: List[Tuple[str, str]] = []
    for line in lines_rand:
        for alphabet in line:
            list_rand.append((alphabet, side_name_dict[alphabet]))

    list_rand_gen: Iterator[Tuple[str, str]] = iter(list_rand)

    # Read each line from final latex file and store as list
    with open(latest_tex_file_path) as texPath:
        lines_tex: List[str] = texPath.readlines()

    barcode_mask: str = r"S[0-9]{3}[0-9]{2}T[0-9]{2}FTO.jpg\}\}&&\\raisebox\{"
    side_mask: str = r"F[0-9]{2}"

    side_name_mask: re.Pattern = re.compile(r"\}\{[a-zA-Z ]*\}\}&")
    
    # Locate the lines with row names per subject
    for big_line in lines_tex:
        if r"\raisebox{-.5\height}{\rotatebox{90}" in big_line:
            side_name: str = side_name_mask.search(big_line).group(0)
            val: Tuple[str, str] = next(list_rand_gen)
            replacement: str = "}{" + val[1] + "Prd" + val[0] + "}}&"
            new_big_line: str = big_line.replace(side_name, replacement)
            lines_tex[lines_tex.index(big_line)] = new_big_line

    # Write the modified lines to a new LaTeX file
    new_file_gen: Iterator[str] = iter(lines_tex)
    new_texfile_name: str = latest_tex_file_path.split("\\")[-1][:-4]
    
    with open(os.path.join("\\".join(latest_tex_file_path.split("\\")[:-1]),
                          f"{new_texfile_name}_randomized_sidenames_revised1.tex"), "w") as f_new:
        while True:
            try:
                f_new.write(next(new_file_gen))
            except StopIteration:
                break
