This file contains a collection of utility functions for file and directory operations, logging, and other common tasks.

## Key Features

    File and directory manipulation
    Logging setup
    File hashing (MD5 and SHA512)
    Backup creation
    Batch file generation

## Main Functions

File Operations

. create_filename_from_basefile: Creates a new file location from a given filename
. getAllFiles: Finds files by mask in a path and subdirectories
. getAllFilesIter: Similar to getAllFiles, but returns a generator
. backupFile: Creates a backup of a file with options for multiple backups
. secureMoveFile: Safely moves a file to a new location, verifying integrity with MD5 hashes
. secureCopyFile: Safely copies a file, creating backups if necessary


Directory Operations

. createDirectory: Creates a directory structure if it doesn't exist
. getAllDirs: Finds directories by mask in a path and subdirectories
. get_immediate_subdirectories: Gets the names of immediate subdirectories


File Information

. getPathDepth: Returns the depth of a given path1
. get_basefilename: Extracts the base filename without path and extension1
. getModificationTime: Gets the last modification time of a file

Hashing

. md5_for_file: Generates an MD5 hash for a given file
. sha512_for_file: Generates a SHA512 hash for a given file

Logging

. createStandardLogger: Sets up a standard logger with file and console handlers

Miscellaneous

. createBatchFile: Creates a batch file with a specified command for a list of files

## Usage
Import the required functions from this utility file to use them in your Python scripts. 

For example:

from Util import getAllFiles, backupFile, md5_for_file

Use the imported functions in your code

files = getAllFiles("/path/to/directory", "*.txt")
backupFile("important_file.txt")
file_hash = md5_for_file("checksum_file.bin")

Dependencies
This utility file requires the following Python libraries:

    pickle
    threading
    typing
    dask
    psutil
    jsonpickle
    numpy
    git (optional)

Ensure these dependencies are installed before using the utility functions.