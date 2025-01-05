"""
This script defines a method `BarcodeReader` to detect barcodes from an image, highlights the barcode's position 
by drawing a rectangle around it, and saves the processed images (masked and highlighted) for verification.

Dependencies:
- `cv2` (OpenCV): Used for image processing.
- `pyzbar.pyzbar.decode`: Used to decode barcodes from images.
- `numpy` (NumPy): Used for numerical operations on image arrays.
- `os`: Used for file path manipulations.

Functions:
- BarcodeReader(path): Detects and decodes barcodes from an image at the given path.

Workflow:
1. **Read the Image**:
   - The image is read using OpenCV (`cv2.imread`) and converted to grayscale for easier processing.
   
    Image Preprocessing:

        The grayscale conversion and binary masking isolate the barcode region for better detection.
        The pixel range [170, 255] in cv2.inRange should be adjusted based on the barcode's contrast and background.
        
        
2. **Create a Mask**:
   - A binary mask is created by thresholding the grayscale image using `cv2.inRange`.
   - This highlights the barcode region by isolating pixel values in the specified range.

3. **Decode Barcodes**:
   - The `decode` function from `pyzbar` is used to extract barcode data from the masked image.
   - If no barcode is detected, the function prints a message and returns `None`.
   
    Barcode Detection:

        pyzbar.pyzbar.decode is robust and can handle various barcode formats (e.g., QR codes, UPC, etc.).
        Multiple barcodes can be detected in a single image, but this implementation processes only the first one.
        
        
4. **Highlight Barcode and Save Results**:
   - If a barcode is detected:
     - The bounding box around the barcode is drawn using `cv2.rectangle`.
     - The masked image and the image with the highlighted barcode are saved in the `bin` directory.
     - The barcode data is printed and returned.

5. **Main Functionality**:
   - If the script is executed directly, it attempts to read a sample image specified in `path_to_image` 
     and calls `BarcodeReader` to process it.

File Output:
- **Masked Image**: A binary image (`_masked.png`) highlighting regions in the threshold range.
- **Highlighted Image**: The original image (`_detected.png`) with a rectangle around the detected barcode.

Notes:
- The barcode data is returned as a byte string.
- The script saves output files in the `bin` directory relative to the current working directory.
- The `cv2.imshow` calls and other unused code are commented out, but they can be enabled for debugging or visualization.
"""

# Importing required libraries
import cv2 
from pyzbar.pyzbar import decode 
import numpy as np
import os

def BarcodeReader(path: str) -> str | None:
    """
    Reads and decodes a barcode from an image at the specified path.

    Args:
    - path (str): The file path of the image to process.

    Returns:
    - str or None: The decoded barcode data if detected, otherwise None.
    """

    # Read the image as a NumPy array
    img = cv2.imread(path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Create a binary mask with pixel values in the range 170 to 255
    mask = cv2.inRange(gray, 170, 255)

    # Get the filename from the path
    fn = path.split("\\")[-1]
    
    # Decode the barcode from the masked image
    detectedBarcodes = decode(mask) 
    
    # Check if barcodes are detected
    if not detectedBarcodes: 
        print("Barcode Not Detected or your barcode is blank/corrupted!") 
        return None
    else: 
        # Process each detected barcode
        for barcode in detectedBarcodes: 
            # Get the bounding box of the barcode
            (x, y, w, h) = barcode.rect 
            
            # Draw a rectangle around the detected barcode
            cv2.rectangle(img, (x-10, y-10), 
                          (x + w+10, y + h+10), 
                          (255, 0, 0), 5) 
            
            # Save the masked and detected images in the `bin` directory
            cv2.imwrite(r"bin\\" + fn + "_masked.png", mask)
            cv2.imwrite(r"bin\\" + fn + "_detected.png", img)
            
            # If the barcode data is not empty, print and return it
            if barcode.data != "": 
                print(barcode.data) 
                return barcode.data

if __name__ == "__main__": 
    # Define the path to a sample image for testing
    path_to_image = r"path_to_images\bin\_57A4711.JPG"
    
    # Call the BarcodeReader function with the sample image path
    BarcodeReader(path_to_image)

