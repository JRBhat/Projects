# QR Code Image Registration and Transformation Project

This project aims to process skewed scanned images, extract QR code coordinates, apply transformations, and register the images using a reference PTX file. The core functionalities include:

1. **QR Code Generation**:
   - **make_quick_qrcode**: Generates a basic QR code and saves it to the specified path.
   - **make_custom_qrcode**: Creates a customizable QR code with options for color, border, and box size.

2. **Image Registration**:
   - **register_image**: Calculates a similarity transform to align a skewed image with a reference using the QR code coordinates.
   - **registration_step**: Executes the registration process, applying the transformation to both the image and its PTX file.
   - **create_final_ptx**: Creates the final PTX file by updating the transformed coordinates in the PTX file.

3. **File Management**:
   - **move_files**: Moves files to different directories (e.g., "bad", "inverted") based on the processing status of the image.

4. **Image Mask Generation**:
   - **generate_masks**: Generates binary masks for QR code extraction in scanned images.

## Features:
- Detect and handle skewed scanned images.
- Apply geometric transformations using similarity and Euclidean transforms.
- Generate and register QR codes and corresponding PTX files.
- Supports custom QR code styling.
- Logging to track the process and handle errors.
- Organizes processed files into different directories based on their status.

## Setup:
1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Modify the paths in the code to point to the appropriate directories for your images and PTX files.

3. Run the main function:
    ```python
    python main.py
    ```

## Directory Structure:
- `SCANS`: Folder containing the scanned images.
- `PIAS`: Folder containing the reference PTX files.
- `output`: Directory where the processed images will be saved.
- `bad`: Directory for images that failed processing.
- `inverted`: Directory for images detected as inverted.

## Requirements:
- Python 3.x
- Dependencies: `scikit-image`, `numpy`, `shutil`, `json`, `logging`, `qrcode`, and other libraries as needed.

## Notes:
- The code assumes that images are in TIFF format.
- The QR code transformation requires at least 3 pairs of coordinates for a valid transformation.
- Logs are written to `app.log` for tracking the process.

## License:
This project is licensed under the MIT License - see the LICENSE file for details.
