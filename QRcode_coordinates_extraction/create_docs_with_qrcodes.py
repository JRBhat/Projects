import xml.etree.ElementTree as ET
from generate_qrcode import make_quick_qrcode
import subprocess
import os
import shutil
from typing import Optional


def update_document_xml(Path_to_xml: str, n: int) -> None:
    """
    Updates the document.xml file by replacing "Proband {n} t0" and "Proband {n+1} t0" 
    in the relevant XML nodes.

    Args:
        Path_to_xml (str): Path to the document.xml file.
        n (int): The current iteration number used to generate the Proband values.

    Returns:
        None
    """
    # reference document.xml - do not change
    tree = ET.parse(Path_to_xml)
    root = tree.getroot()
    
    if n > 1:
        root[0][0][2][2][1][0][0].text = str(f"Proband {n} t0")
        root[0][0][7][2][1][0][0].text = str(f"Proband {n+1} t0")
        
    tree.write(Path_to_xml)
    print(f"document.xml updated with Proband {n} and Proband {n+1}")


def zip_contents(path_to_zip: str, n: int) -> None:
    """
    Zips the contents of a folder and names the zip file based on the Proband iteration.

    Args:
        path_to_zip (str): Path to the folder containing the content to zip.
        n (int): The current iteration number used in the zip file name.

    Returns:
        None
    """
    proc = subprocess.Popen(f"d: && cd {path_to_zip} && zip -r test_doc_prob{n}and{n+1}.zip *", shell=True)
    proc.wait()
    print(f"Contents of {path_to_zip} archived successfully")


def main() -> None:
    """
    Main function that orchestrates the entire process of updating XML, generating QR codes, 
    zipping files, and moving them to the output directory.

    Args:
        None

    Returns:
        None
    """
    output_path = r"D:\Code\Codebase_Bha\Dev_Project22_QRCode_reader_coordnates_extraction\bin\test\results"
    Path_to_docxml = r"D:\Code\Codebase_Bha\Dev_Project22_QRCode_reader_coordnates_extraction\bin\test\latest_doc\word\document.xml"
    path_to_qrcode_img = r"D:\Code\Codebase_Bha\Dev_Project22_QRCode_reader_coordnates_extraction\bin\test\latest_doc\word\media\image1.png"
    folderpath_to_zip = r"D:\Code\Codebase_Bha\Dev_Project22_QRCode_reader_coordnates_extraction\bin\test\latest_doc"
    
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    
    i = 1
    while i < 56:
        
        # change the text in the xml file
        if i > 1:
            update_document_xml(Path_to_docxml, i)
        
        # replace qrcode image with new one
        make_quick_qrcode(f"Pos 1", path_to_qrcode_img)

        # zip contents
        zip_contents(folderpath_to_zip, i)
        
        # change extension and move file to output folder
        if f"test_doc_prob{i}and{i+1}.zip" in os.listdir(folderpath_to_zip):
            path_with_oldname = os.path.join(folderpath_to_zip, f"test_doc_prob{i}and{i+1}.zip")
            path_with_newname = path_with_oldname.replace(".zip", ".docx") 
            os.rename(path_with_oldname, path_with_newname)
            final_path = os.path.join(output_path, path_with_newname.split("\\")[-1])
            shutil.move(path_with_newname, final_path)
            print("docx successfully moved to output folder")
        
        i += 2


if __name__ == "__main__":
    main()
