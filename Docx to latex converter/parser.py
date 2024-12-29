from docx import Document as dok
from typing import List, Dict

def parse_document(doc_filename: str) -> Dict[str, any]:
    """
    Parses a Word document (.docx) into structured content: paragraphs and tables.

    :param doc_filename: Path to the .docx file
    :return: A dictionary containing parsed content
    """
    document = dok(doc_filename)
    
    # Collect all paragraphs
    all_paragraphs = document.paragraphs
    print(f"No of paragraphs read: {len(all_paragraphs)}")

    # Clean and store paragraphs
    names_explanation_list = [para.text for para in all_paragraphs if para.text.strip() != ""]

    # Collect all tables
    all_tables = document.tables
    dict_table = {}

    # Process each table and store their content
    for obj_num, table in enumerate(all_tables, start=1):
        list_for_table = f"table_{obj_num}_list"
        dict_table[list_for_table] = []
        if obj_num == len(all_tables):
            dict_table[f"table_{obj_num}_para_list"] = []
            dict_table[f"table_{obj_num}_col_1_para_list"] = []

        # Process rows in tables
        for row in table.rows:
            for cell in row.cells:
                dict_table[list_for_table].append(cell.text)
    
    # Return structured content
    return {
        'names_explanation_list': names_explanation_list,
        'dict_table': dict_table,
        'all_tables': all_tables
    }
