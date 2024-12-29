from utils import escape_special_chars, itemize_function, subsection_with_explanation, table_description
from typing import Dict, List

def generate_latex_document(content: Dict[str, any], doc_filename: str) -> str:
    """
    Generates a LaTeX document from the parsed Word document content.

    :param content: A dictionary containing parsed content
    :param doc_filename: Path to the original document (used to generate .tex filename)
    :return: The path to the generated .tex file
    """
    names_explanation_list = content['names_explanation_list']
    dict_table = content['dict_table']
    all_tables = content['all_tables']

    # Clean the table content
    table_X_col_1_para_list = content['dict_table'][f"table_{len(all_tables)}_col_1_para_list"]
    clean_table_X_col_1_para_list = clean_list(table_X_col_1_para_list)

    # Extract title from the first item
    title = names_explanation_list.pop(0)

    # Create the LaTeX file
    tex_filename = f"{doc_filename[:-5]}.tex"
    with open(tex_filename, "w") as TxF:
        TxF.write("\\documentclass[a4paper, 12pt]{article}\n")
        TxF.write("\\begin{document}\n")
        TxF.write(f"\\section*{{\\huge {escape_special_chars(title)}}}\n")

        # Write paragraphs with explanations
        z = 0
        while z < len(names_explanation_list):
            TxF.write(f"\\section{{{escape_special_chars(names_explanation_list[z])}}}\n")
            TxF.write(f"{escape_special_chars(names_explanation_list[z + 1])}\n")
            z += 2

        # Write tables and associated descriptions
        i, j = 0, 0
        while i < len(names_explanation_list) and j < len(all_tables):
            subsection_with_explanation(TxF, names_explanation_list[i], names_explanation_list[i + 1])
            table_description(
                TxF, dict_table[f"table_{j + 1}_list"], 
                dict_table[f"table_{len(all_tables)}_para_list"], 
                clean_table_X_col_1_para_list
            )
            i += 2
            j += 1

        TxF.write("\\thispagestyle{empty}\n")
        TxF.write("\\end{document}\n")

    return tex_filename
