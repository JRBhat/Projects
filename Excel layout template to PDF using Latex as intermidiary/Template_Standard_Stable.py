import Internal_Imports_Stable as Imp 
from Latex_File_Create_Stable import create_final_latex_file
from Common_Functions_Stable import create_Latex_document
from typing import List, Iterator, Tuple

def standardize(
    area_code_list: List[str],
    time_code_list: List[str],
    area_sorted: List[str],
    time_sorted: List[str],
    sub_sorted: List[str],
    filepaths: List[str],
    filenamelist: List[str],
    rownames: List[str],
    colnames: List[str],
    random_iter: Iterator[Tuple[str, str]],
    Imp: Imp
) -> str:
    """
    Standard template - User needs to only change the column and row names.

    This function generates a LaTeX file with a standardized template using the provided 
    area, time, and subject information, along with file paths and filenames. The layout 
    of the generated document is customized according to the number of rows and columns.

    Args:
        area_code_list (List[str]): List of area codes.
        time_code_list (List[str]): List of time codes.
        area_sorted (List[str]): Sorted list of area names.
        time_sorted (List[str]): Sorted list of time points.
        sub_sorted (List[str]): Sorted list of subject IDs.
        filepaths (List[str]): List of file paths corresponding to the data.
        filenamelist (List[str]): List of filenames associated with the file paths.
        rownames (List[str]): List of row names for the LaTeX table.
        colnames (List[str]): List of column names for the LaTeX table.
        random_iter (Iterator[Tuple[str, str]]): Iterator of tuples containing randomization data (file paths and random codes).
        Imp (Imp): An instance of the `Internal_Imports_Stable` module containing necessary import details.

    Returns:
        str: The path to the generated LaTeX file.
    """
    nr_col = len(time_code_list)
    nr_row = len(area_code_list)

    max_height = round(1.0 / (1.25 * nr_row), 2) 
    
    next_label_count = "".join(rownames).count("next")
    if next_label_count > 0:
        max_height = round((1.0 * next_label_count) / (1.25 * nr_row), 2)

    max_width = round(1.0 / (1.5 * nr_col), 2)

    # Create LaTeX document with standardized layout
    lax_document, new_page_alert = create_Latex_document(
        colnames, rownames, sub_sorted, max_height, max_width,
        area_sorted, time_sorted, filepaths, filenamelist, 
        Type="Standard", RandomList=random_iter
    )

    # Generate final LaTeX file
    std_tex_file = create_final_latex_file(
        Imp.studynumber, Imp.header, Imp.pagestyle, Imp.hypersetup, 
        lax_document, new_page_alert, colnames, Imp.Test_type, draft=Imp.draft_flag
    )

    return std_tex_file
