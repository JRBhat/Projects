from typing import List

def escape_special_chars(text: str) -> str:
    """
    Escapes special LaTeX characters in the given text.

    :param text: String to escape
    :return: String with special characters escaped for LaTeX
    """
    replacements = {
        "_": "\\_ ",
        "&": "\\& ",
        "$": "\\$ ",
        "%": "\\% ",
        "{": "\\{ ",
        "}": "\\} ",
        "#": "\\# ",
        "~": "\\textasciitilde ",
        "^": "\\textasciicircum ",
        "\\": "\\textbackslash "
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text


def clean_list(table_list: List[str]) -> List[str]:
    """
    Filters elements without white spaces and appends them to a new list.

    :param table_list: Old list with strings with white spaces
    :return: List containing strings without spaces
    """
    return [elem for elem in table_list if elem.strip()]


def itemize_function(table_paragraph_list: List[str]) -> List[str]:
    """
    Converts a list of paragraphs into LaTeX 'itemize' style bullet points.

    :param table_paragraph_list: List of paragraphs from a table
    :return: List of LaTeX-formatted bullet points
    """
    itemize_list = ["\\begin{itemize}\n"]
    while table_paragraph_list:
        if "=" in table_paragraph_list[0]:
            itemize_list.append(f"\t\\item {escape_special_chars(table_paragraph_list[0])}\n")
            table_paragraph_list.pop(0)
            if not table_paragraph_list or ":" in table_paragraph_list[0]:
                break
        else:
            table_paragraph_list.pop(0)
    itemize_list.append("\\end{itemize}\n")
    return itemize_list


def subsection_with_explanation(obj, Heading: str, Description: str) -> None:
    """
    Creates a subsection with a heading and paragraph as description.

    :param obj: LaTeX file object used by the write method
    :param Heading: Title of the section
    :param Description: Description paragraph of that section
    """
    obj.write(f"\\section{{{escape_special_chars(Heading)}}}")
    obj.write(f"{escape_special_chars(Description)}\n")


def table_description(obj, table_list: List[str], table_para_list: List[str], table_col_para_list: List[str]) -> None:
    """
    Writes the contents from each table to the LaTeX file object in LaTeX syntax.

    :param obj: The LaTeX file object
    :param table_list: List containing table data
    :param table_para_list: List of paragraphs from the last table's cells
    :param table_col_para_list: List of paragraphs from the first column of the last table
    """
    obj.write("\\begin{description}\n")
    k = 0
    while k < len(table_list):
        if (table_list[len(table_list) - 1] and "=" in table_list[k + 1] and ":" in table_list[k]):
            obj.write(f"\\item[\\small {escape_special_chars(table_col_para_list[k])}]\\mbox{}\n")
            obj.write(f"{escape_special_chars(table_para_list[k])}\\newline\n")
            for para_item in itemize_function(table_para_list):
                obj.write(para_item)
        else:
            obj.write(f"\\item[\\small {escape_special_chars(table_list[k])}] {escape_special_chars(table_list[k + 1])}\n")
        k += 2
    obj.write("\\end{description}\n")
