"""
This script processes images by applying effects (blur, blacken, or smudge) to specific regions defined by bounding boxes. 
Bounding box coordinates are read from a JSON (.ptx) file, and the specified effect is applied to the region of interest in the image.

Key functionalities:
1. Reads bounding box coordinates from a JSON file.
2. Applies effects like pixelation, blackening, or smudging to the bounding box area in an image.
3. Saves the processed image with the effect applied.

Usage:
- Place your images and corresponding .ptx files in the specified directory.
- Configure the effects, paths, and parameters as needed.
"""


import cv2
import numpy as np
import json
import os
from typing import Tuple, List


def read_bbox_from_ptx(ptx_path: str) -> Tuple[int, int, int, int]:
    """
    Read bounding box coordinates from a JSON file.

    :param ptx_path: Path to the .ptx file containing the bounding box data.
    :return: A tuple (x, y, w, h) representing the bounding box coordinates.
    :raises ValueError: If the JSON structure is invalid or the 'contour' key is missing.
    """
    with open(ptx_path, 'r') as f:
        data = json.load(f)
    
    if not data or 'contour' not in data[0]:
        raise ValueError("Invalid JSON structure or missing 'contour' key")
    
    contour: List[List[int]] = data[0]['contour']
    x_coords = [point[0] for point in contour]
    y_coords = [point[1] for point in contour]
    
    x = min(x_coords)
    y = min(y_coords)
    w = max(x_coords) - x
    h = max(y_coords) - y
    
    return (x, y, w, h)


def pixelate(image: np.ndarray, pixel_size: int = 10) -> np.ndarray:
    """
    Pixelate the given image by resizing it to a smaller resolution and back.

    :param image: The input image as a NumPy array.
    :param pixel_size: The size of the pixelation squares (default is 10).
    :return: A pixelated version of the input image as a NumPy array.
    """
    h, w = image.shape[:2]
    
    # Resize image to a small size
    temp = cv2.resize(image, (w // pixel_size, h // pixel_size), interpolation=cv2.INTER_CUBIC)
    
    # Resize back to original size
    return cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)


def process_bounding_box(
    image_path: str,
    bbox_coords: Tuple[int, int, int, int],
    effect: str = 'blur',
    intensity: int = 1,
    pixel_size: int = 175
) -> np.ndarray:
    """
    Apply an effect (blur, blacken, or smudge) to a specific bounding box area in an image.

    :param image_path: Path to the input image file.
    :param bbox_coords: A tuple (x, y, w, h) representing the bounding box coordinates.
    :param effect: The effect to apply ('blur', 'blacken', or 'smudge') (default is 'blur').
    :param intensity: The intensity of the effect (used for blur and smudge) (default is 1).
    :param pixel_size: Pixel size for the pixelation effect (used for 'blur') (default is 175).
    :return: The processed image as a NumPy array.
    :raises ValueError: If the image cannot be read or an invalid effect is specified.
    """
    # Read the image
    image = cv2.imread(image_path)
    
    if image is None:
        raise ValueError("Unable to read the image. Please check the file path.")
    
    # Extract bounding box coordinates
    x, y, w, h = bbox_coords
    
    # Extract the region of interest (ROI)
    roi = image[y:y+h, x:x+w]
    
    if effect == 'blur':
        # Apply pixelation to the ROI
        processed_roi = pixelate(roi, pixel_size)
        
    elif effect == 'blacken':
        # Create a black rectangle of the same size as ROI
        processed_roi = np.zeros(roi.shape, dtype=np.uint8)
    
    elif effect == 'smudge':
        # Create a smudge effect by applying motion blur
        kernel_size = intensity
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[int((kernel_size-1)/2), :] = np.ones(kernel_size)
        kernel = kernel / kernel_size
        processed_roi = cv2.filter2D(roi, -1, kernel)
    
    else:
        raise ValueError("Invalid effect. Choose 'blur', 'blacken', or 'smudge'.")
    
    # Place the processed ROI back into the image
    image[y:y+h, x:x+w] = processed_roi
    
    return image


if __name__ == "__main__":
    PATH = r"path_to_images"
    EXTN = ".TIF"
    
    for fn in os.listdir(PATH):
        if fn.endswith(EXTN):
            effects = ['blur']  # Add other effects like 'blacken' or 'smudge' as needed.
            ptx_path = os.path.join(PATH, fn.replace(EXTN, ".ptx"))
            
            try:
                # Read bounding box coordinates from JSON
                bbox_coords = read_bbox_from_ptx(ptx_path)
                
                image_path = os.path.join(PATH, fn)
                for effect in effects:
                    result = process_bounding_box(image_path, bbox_coords, effect=effect)
                    
                    # Save the result
                    output_path = os.path.join(PATH, f"{fn}_{effect}ed3{EXTN}")
                    cv2.imwrite(output_path, result)
                    print(f"{effect.capitalize()}ed image saved as '{output_path}'")
            
            except Exception as e:
                print(f"An error occurred: {str(e)}")
