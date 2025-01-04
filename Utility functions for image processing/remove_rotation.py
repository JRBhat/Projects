"""
This script processes all `.cr2` files in specified directories by running the `exiftool` 
command to reset their image orientation metadata. Any errors during the process 
are logged to the console.
"""

import os
import subprocess
from typing import List

def main() -> None:
    """
    Processes all `.cr2` files in the specified directories using `exiftool` to reset 
    image orientation metadata. Outputs success or error messages for each file.

    :raises Exception: If the subprocess encounters an error.
    """
    # List of directories containing `.cr2` files
    PATHS: List[str] = [r"path_to_images"]
    
    for path in PATHS:
        for filename in os.listdir(path):
            if filename.endswith(".cr2"):
                file_path = os.path.join(path, filename)
                try:
                    # Run exiftool command to reset orientation metadata
                    proc = subprocess.Popen(
                        f"C:\\scripts\\Skripte\\exiftool.exe -IFD0:Orientation=1 -EXIF:Orientation=1 {file_path}", 
                        shell=True,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE
                    )
                    stdout, stderr = proc.communicate()
                    
                    # Log success or error messages
                    if proc.returncode != 0:
                        print(f"Error processing {file_path}: {stderr.decode().strip()}")
                    else:
                        print(f"Processed {file_path}: {stdout.decode().strip()}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    main()
