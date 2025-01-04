import os
import shutil
from typing import List

PATHS: List[List[str]] = [
    [
        r"D:\STUDIES\23.0019_AntiAkne\Vivascope\230019_export_clean_t1",
        r"D:\STUDIES\23.0019_AntiAkne\Vivascope\piased_t1\block_imgs_out"
    ],
    [
        r"D:\STUDIES\23.0019_AntiAkne\Vivascope\230019_export_clean_t57",
        r"D:\STUDIES\23.0019_AntiAkne\Vivascope\piased_t57\block_imgs_out"
    ]
]

def copy_viva_block_images(paths: List[List[str]]) -> None:
    """
    Copies VivaBlock images from source directories to destination directories.

    Args:
        paths (List[List[str]]): A list of lists, where each inner list contains
                                 the source and destination directory paths.

    The function walks through the source directories, identifies files containing
    "VivaBlock" in their names within the "VivaBlock #1" subdirectory, and copies
    these files to the corresponding destination directory.
    """
    for path_list in paths:
        for root, dirs, files in os.walk(path_list[0]):
            if root.split("\\")[-1] == "VivaBlock #1":
                fn = [fn for fn in os.listdir(root) if "VivaBlock" in fn][0]
                print(fn, root)
                shutil.copy(os.path.join(root, fn), os.path.join(path_list[1], fn))

if __name__ == "__main__":
    copy_viva_block_images(PATHS)
