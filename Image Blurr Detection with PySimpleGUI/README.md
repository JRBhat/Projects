# Custom Image Processing and Directory Monitoring for Clinical Trials

This project is designed to handle image processing tasks and directory monitoring for clinical trials in skin care and cosmetic product testing. It is particularly focused on verifying image quality, including barcode verification, image focus, and white card status. The system allows for custom pop-ups and automated actions based on real-time directory changes and image analysis.

## Features

- **Custom Pop-ups**: Displays custom pop-ups based on the focus status, barcode verification, and white card status in the image.
- **Directory Monitoring**: Monitors a directory for file changes and updates the application accordingly.
- **Barcode Extraction**: Extracts and formats barcodes from the images for verification.
- **Threshold-based Actions**: Uses predefined thresholds to determine if images are in focus and if the white card is detected, triggering actions such as showing warnings or prompts to the user.
- **Automated Image Processing**: Handles image slicing and automated checks to validate the quality and consistency of images.
  
## Dependencies

- `PySimpleGUI`: For creating interactive pop-up windows and UI elements.
- `win32file`, `win32con`, `win32event`: For directory monitoring and detecting file changes.
- `re`: For regular expression-based barcode extraction.
- `os`: For interacting with the file system.
- `logging`: For logging the events and actions performed.

## Usage

1. **Setup**:
   - Clone the repository.
   - Install the required Python packages using `pip`:
     ```bash
     pip install PySimpleGUI pywin32
     ```

2. **Run the Program**:
   - Run the Python script.
   - Enter the directory path to monitor.
   - Set the focus and white card thresholds.
   - Start the monitoring and follow the prompts to interact with the system.

3. **Interacting with the Pop-up**:
   - The pop-up window will display information about the image, such as focus status, barcode, and white card status.
   - You can choose to confirm if the barcode is correct or continue with the image processing.

4. **Directory Monitoring**:
   - The system will monitor the directory for changes (like new files or deletions) and automatically respond to those changes, including closing the pop-up or continuing with the workflow.

## Functions

- **`custom_popup`**: Creates a custom pop-up based on the image and directory status, asking for user input for barcode verification and image quality.
- **`watch_dir_simple`**: Monitors a directory for file changes and returns a status based on changes.
- **`main`**: The main function that initializes the program, handles user input for directory paths and thresholds, and starts the directory monitoring.

## Notes

- The program uses a simple thresholding mechanism for image focus and white card detection.
- The pop-up window will appear based on the image focus and white card detection status, with different color schemes and messages indicating the status.
