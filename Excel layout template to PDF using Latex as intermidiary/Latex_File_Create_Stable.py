import os
from typing import List, Dict, Optional

def create_final_latex_file(
    studynumber: str, 
    header: str, 
    pagestyle: str, 
    hypersetup: str, 
    lax_document: List[Dict], 
    new_page_alert: int, 
    colnames: List[str], 
    Testtype: str, 
    draft: str = 'False'
) -> str:
    """
    Creates the final LaTeX file which can then be converted to PDF.

    Args:
        studynumber (str): The study number to be included in the filename and document.
        header (str): The LaTeX header to be included in the document.
        pagestyle (str): The LaTeX page style to be included in the document.
        hypersetup (str): The LaTeX hyper setup for PDF export.
        lax_document (List[Dict]): A list of dictionaries, each representing a page with tables and headings.
        new_page_alert (int): The flag to indicate when a new page should be added in the LaTeX file.
        colnames (List[str]): The list of column names to be used in the LaTeX table.
        Testtype (str): The type of the test for naming the file.
        draft (str, optional): A flag ('True' or 'False') to determine if the file should be in draft mode. Defaults to 'False'.

    Returns:
        str: The file path of the generated LaTeX file.

    """
    # If draft mode is ON; only image paths printed in PDF, loading the images is skipped (useful for testing purposes)
    if draft == 'True':
        with open(f"{studynumber}_{Testtype}_image_overview_draft.tex", "w") as f:
            f.write(header)
            f.write(pagestyle)
            f.write(hypersetup + "\n") 

            f.write(r"\begin{document}" + "\n\n")

            for pageno, lax_page in enumerate(lax_document):
                lax_table = lax_page['table'][pageno]
                f.write(r"{\Large %s}\\[0.2cm]" % (lax_page['heading'][pageno]) + "\n")
                f.write(r"\begin{tabular}{%s}" % ("".join(['cc'] * (len(colnames)))) + "\n")
                f.write(lax_page['col_name_block'] + "\n")
                for lax_row in lax_table:
                    f.write(lax_row + "\n")

                if new_page_alert == 0:
                    f.write(r"\end{tabular}" + "\n")
                    if 'end' not in lax_table and not (pageno == len(lax_document) - 1):
                        f.write(r"\newpage" + "\n\n")

            f.write(r"\end{document}" + "\n")
        tex_filename = os.path.join(os.getcwd(), f"{studynumber}_{Testtype}_image_overview_draft.tex")

    # Original; where all photos are downloaded; final PDF generated
    elif draft == 'False':
        with open(f"{studynumber}_{Testtype}_image_overview.tex", "w") as f:
            f.write(header)
            f.write(pagestyle)
            f.write(hypersetup + "\n")

            f.write(r"\begin{document}" + "\n\n")

            for pageno, lax_page in enumerate(lax_document):
                lax_table = lax_page['table'][pageno]
                f.write(r"{\Large %s}\\[0.2cm]" % (lax_page['heading'][pageno]) + "\n")
                f.write(r"\begin{tabular}{%s}" % ("".join(['cc'] * (len(colnames)))) + "\n")
                f.write(lax_page['col_name_block'] + "\n")
                for lax_row in lax_table:
                    f.write(lax_row + "\n")

                f.write(r"\end{tabular}" + "\n")
                if 'end' not in lax_table and not (pageno == len(lax_document) - 1):
                    f.write(r"\newpage" + "\n\n")
            f.write(r"\end{document}" + "\n")

        tex_filename = os.path.join(os.getcwd(), f"{studynumber}_{Testtype}_image_overview.tex")

    return tex_filename
