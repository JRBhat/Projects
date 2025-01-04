import os
import shutil

def rename_files_in_directory(path: str) -> None:
    """
    Renames files in the specified directory based on certain conditions.

    Args:
        path (str): The directory path containing the files to be renamed.

    The function iterates through the files in the specified directory,
    and renames them based on the presence of specific substrings ("kt1" or "kt2")
    in their filenames.
    """
    for fn in os.listdir(path):
        if "kt1" in fn:
            nfn = fn.replace("S", "S0").replace("_c", "F01T01_c")
            print(fn, nfn)
            os.rename(os.path.join(path, fn), os.path.join(path, nfn))
        elif "kt2" in fn:
            nfn = fn.replace("S", "S0").replace("_c", "F01T02_c")
            print(fn, nfn)
            os.rename(os.path.join(path, fn), os.path.join(path, nfn))

def main() -> None:
    """
    Main function to rename files in the specified directory.
    """
    PATH = r"path_to_images"
    rename_files_in_directory(PATH)

if __name__ == "__main__":
    main()
