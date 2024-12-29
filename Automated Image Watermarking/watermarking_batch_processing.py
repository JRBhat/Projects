import os
import subprocess
import shutil
import time
from typing import List

path = r"path to images to be watermarked"  # Location of images to be watermarked
bat_source = r"watermarking.bat"  # Batch file location

count = 0
detected: List[str] = []  # List to store detected files
shortcuts: List[str] = []  # List to store shortcut files

# Checks all file extensions and renames them to the correct format
for dirpath, dirname, files in os.walk(path):
    if len(files) != 0:
        for file in files:
            if file.endswith('.JPG') or file.endswith('.JPEG') or file.endswith('.jpeg'):
                base = os.path.splitext(file)[0]
                os.rename(os.path.join(dirpath, file), os.path.join(dirpath, base + '.jpg'))
                detected.append(os.path.join(dirpath, file))

            elif file.endswith('.TIF') or file.endswith('.TIFF') or file.endswith('tiff'):
                base = os.path.splitext(file)[0]
                os.rename(os.path.join(dirpath, file), os.path.join(dirpath, base + '.tif'))
                detected.append(os.path.join(dirpath, file))

            elif file.endswith('.PNG'):
                base = os.path.splitext(file)[0]
                os.rename(os.path.join(dirpath, file), os.path.join(dirpath, base + '.png'))
                detected.append(os.path.join(dirpath, file))

            elif file.endswith('.lnk'):
                shortcuts.append(os.path.join(dirpath, file))

print(detected)
print(shortcuts)

last_dirpathname = ""

# Recursively iterates over each directory and sub-directories and watermarks images that comply to image extensions
time_start = time.perf_counter()

for dirpath, dirname, files in os.walk(path):
    if len(files) != 0:
        if "_watermarked" in dirpath or "_watermarked" in dirname:
            print(f"Skipped path: {dirpath}")
            continue
        else:
            for file in files:
                if ('.jpg' in file or '.png' in file or 'tif' in file) and count == 0:
                    shutil.copy(bat_source, dirpath)
                    cmdline = os.path.join(dirpath, 'watermarking.bat')
                    subprocess.call(cmdline, cwd=dirpath)
                    temp_path = dirpath
                    last_dirpathname = dirpath
                    count = 1
                    break

                elif ('.jpg' in file or '.png' in file or 'tif' in file) and count == 1:
                    shutil.move(os.path.join(temp_path, 'watermarking.bat'), dirpath)
                    cmdline1 = os.path.join(dirpath, 'watermarking.bat')
                    subprocess.call(cmdline1, cwd=dirpath)
                    temp_path = dirpath
                    last_dirpathname = dirpath
                    break

if os.path.exists(os.path.join(last_dirpathname, "watermarking.bat")):
    os.remove(os.path.join(last_dirpathname, "watermarking.bat"))
else:
    print("The file does not exist")

time_stop = time.perf_counter()
in_minutes = (time_stop - time_start) / 60
in_hours = in_minutes / 60
if in_minutes >= 60:
    print(f"Total time: {in_hours}")
print(f"Total time: {in_minutes}")
