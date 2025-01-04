import os
import shutil
from typing import List

def copy_macroscopic_images(basepath: str, outpath: str) -> None:
    """
    Copies macroscopic images from the specified base directory to the output directory.

    Args:
        basepath (str): The base directory path containing the macroscopic images.
        outpath (str): The output directory path where the images will be copied.

    The function walks through the base directory, identifies files containing
    "v0000000" in their names within the "Macroscopic Images #1" subdirectory,
    and copies these files to the output directory with a modified filename.
    """
    if not os.path.isdir(outpath):
        os.mkdir(outpath)

    for root, dirs, files in os.walk(basepath):
        if root.split("\\")[-1] == "Macroscopic Images #1":
            fn = [fn for fn in os.listdir(root) if "v0000000" in fn][0]
            print(root, fn, root.split("\\")[-3])
            subj_id = root.split("\\")[-3]
            shutil.copy(os.path.join(root, fn), os.path.join(outpath, subj_id + "_" + fn))

def main() -> None:
    """
    Main function to copy macroscopic images from the base directory to the output directory.
    """
    BASEPATH = r"path\230019_export_clean_t57"
    OUTPATH = os.path.join(r"path\piased_t57", "macros_out")
    copy_macroscopic_images(BASEPATH, OUTPATH)

if __name__ == "__main__":
    main()
