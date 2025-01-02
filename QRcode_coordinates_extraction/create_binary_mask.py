import cv2
import numpy as np
import json
import os
from typing import List


def create_circle_mask(json_file_path: str, image_path: str, circle_ids: List[int]) -> np.ndarray:
    """
    Creates a binary mask of circles specified in a JSON file.

    Args:
        json_file_path (str): The path to the JSON file containing circle data.
        image_path (str): The path to the image used for dimensions.
        circle_ids (List[int]): A list of circle IDs to be included in the mask.

    Returns:
        np.ndarray: A binary mask with circles drawn on it.

    Raises:
        ValueError: If the image file cannot be loaded.
    """
    # Load the image to get its dimensions
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found or unable to read the image file.")
    image_height, image_width = image.shape[:2]

    # Load the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Create a blank binary mask with the same dimensions as the image
    mask = np.zeros((image_height, image_width), dtype=np.uint8)

    # Process each circle entry based on the provided IDs
    for entry in data:
        if entry['id'] in circle_ids:
            radii = entry['radius']
            contours = entry['contour']
            
            # Draw circles on the mask
            for (x, y), radius in zip(contours, radii):
                cv2.circle(mask, (x, y), radius, (255), thickness=-1)  # 255 for white (1 in binary)

    return mask


# Example usage
json_file_path = r"D:\Code\Codebase_Bha\Dev_Project22_QRCode_reader_coordnates_extraction\SCANS\test_good\S700F99T99REG.ptx"  # Path to your JSON file
image_path = r"D:\Code\Codebase_Bha\Dev_Project22_QRCode_reader_coordnates_extraction\SCANS\test_good\S700F99T99REG.tiff"  # Path to your image file

circle_ids = [2, 3]  # IDs of the circles you want to draw

# Create the binary mask
binary_mask = create_circle_mask(json_file_path, image_path, circle_ids)

# Save or display the mask
cv2.imwrite(os.path.join("\\".join(image_path.split("\\")[:-1]), image_path.split("\\")[-1].replace(".tiff", "_binary.tiff")), binary_mask)
# cv2.imshow('Mask', binary_mask)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
