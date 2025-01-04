"""
This script scans a directory for subdirectories and files, collects their extensions and directory names, 
and appends directory names as prefixes to file extensions. The updated names are saved, and a log file is 
created to record directory names, extensions, and any errors encountered during the renaming process.

Key functionalities:
1. Collects all unique directory names and file extensions in the specified path.
2. Renames files by prefixing the parent directory name to their extensions.
3. Logs the results, including any errors, to a log file.
"""


import os
import sys
from typing import Set

def collect_dirnames_and_extensions(path: str) -> tuple[Set[str], Set[str]]:
    """
    Collects all unique directory names and file extensions from a given path.

    :param path: Path to scan for directories and files.
    :return: A tuple containing a set of directory names and a set of file extensions.
    """
    dirname_set: Set[str] = set()
    extensions: Set[str] = set()

    for dirpath, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            dirname_set.add(dirname)
        for file in filenames:
            file_extension = os.path.splitext(file)[1]
            extensions.add(file_extension)

    return dirname_set, extensions


def rename_files_with_prefix(path: str, log_file_path: str) -> None:
    """
    Renames files in the specified path by prefixing the directory name (or a shortened version) 
    to their file extensions. Logs errors and successful operations to a log file.

    :param path: Path to scan for files to rename.
    :param log_file_path: Path to the log file.
    """
    errors = 0

    for dirpath, _, filenames in os.walk(path):
        for fn in filenames:
            ext = os.path.splitext(fn)[-1]
            dir_name = os.path.basename(dirpath)

            # Prefix the directory name or its first 6 characters to the extension
            if len(dir_name) <= 5:
                new_fn = fn.replace(ext, f".{dir_name}{ext}")
            else:
                new_fn = fn.replace(ext, f".{dir_name[:6]}{ext}")

            try:
                os.rename(os.path.join(dirpath, fn), os.path.join(dirpath, new_fn))
            except Exception as e:
                with open(log_file_path, "a+") as fl:
                    fl.write(f"Error renaming {fn}: {e}\n")
                errors = 1

    # Log success or errors
    with open(log_file_path, "a+") as fl:
        if errors == 0:
            fl.write("OK\n")


def main() -> None:
    """
    Main function to execute the script:
    1. Reads the input directory path (either from command-line arguments or a default path).
    2. Scans the directory for unique subdirectory names and file extensions.
    3. Renames files in the directory based on their parent directory names.
    4. Logs the results to a log file.
    """
    # Read path from command-line arguments or use default
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(f"Received command-line argument: {path}")
    else:
        print("No command-line argument provided. Using default path.")
        path = r"D:\test_backup"

    # Prepare log file
    log_path = os.path.dirname(path)
    study_file_name = os.path.basename(path)
    log_file_name = f"{study_file_name}_renaming.log"
    log_file_path = os.path.join(log_path, log_file_name)

    # Collect directory names and file extensions
    dirname_set, extensions = collect_dirnames_and_extensions(path)

    # Print collected data
    print("Directory names found:", dirname_set)
    print("Extensions found:", extensions)

    # Log collected data
    with open(log_file_path, "a+") as fl:
        print("Directory names found:", dirname_set, file=fl)
        print("Extensions found:", extensions, file=fl)

    # Rename files with directory prefixes
    rename_files_with_prefix(path, log_file_path)


if __name__ == "__main__":
    main()
