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
                cv2.circle(mask, (int(x), int(y)), radius, (255), thickness=-1)  # 255 for white (1 in binary)

    return mask


def overlay_mask_on_image(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Overlays a binary mask on an image with transparency.

    Args:
        image (np.ndarray): The original image to overlay the mask onto.
        mask (np.ndarray): The binary mask to overlay.

    Returns:
        np.ndarray: The image with the mask overlaid.
    """
    # Convert the mask to a 3-channel image
    mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Create a semi-transparent overlay
    overlay = cv2.addWeighted(image, 0.7, mask_colored, 0.3, 0)
    
    return overlay


def draw_circles_on_image(image: np.ndarray, json_file_path: str, circle_ids: List[int]) -> np.ndarray:
    """
    Draws circles on an image based on the provided circle IDs from a JSON file.

    Args:
        image (np.ndarray): The image to draw circles on.
        json_file_path (str): The path to the JSON file containing circle data.
        circle_ids (List[int]): A list of circle IDs to be drawn.

    Returns:
        np.ndarray: The image with circles drawn on it.
    """
    # Load the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Draw circles directly on the image
    for entry in data:
        if entry['id'] in circle_ids:
            radii = entry['radius']
            contours = entry['contour']
            
            for (x, y), radius in zip(contours, radii):
                cv2.circle(image, (int(x), int(y)), radius, (0, 255, 0), thickness=2)  # Green circles

    return image


def generate_masks(image_path: str, outpath: str) -> None:
    """
    Generates a binary mask, an overlay image, and an image with circles drawn on it.

    Args:
        image_path (str): The path to the image for which the masks and overlay are generated.
        outpath (str): The directory where the generated files will be saved.
    """
    if not os.path.exists(outpath):
        os.mkdir(outpath)
        
    json_file_path = image_path.replace(".tif", ".ptx")
    circle_ids = [2, 3]  # IDs of the circles you want to draw

    # Load the original image
    original_image = cv2.imread(image_path)

    # Create the binary mask
    binary_mask = create_circle_mask(json_file_path, image_path, circle_ids)

    # Save the binary mask
    cv2.imwrite(os.path.join(outpath, image_path.split("\\")[-1].replace(".tif", "_binary.tif")), binary_mask)

    # Create an overlay with the mask
    overlay_image = overlay_mask_on_image(original_image.copy(), binary_mask)

    # Save the overlay image
    cv2.imwrite(os.path.join(outpath, image_path.split("\\")[-1].replace(".tif", "_overlay.tif")), overlay_image)

    # Draw circles on the original image
    image_with_circles = draw_circles_on_image(overlay_image, json_file_path, circle_ids)

    # Save the image with circles
    cv2.imwrite(os.path.join(outpath, image_path.split("\\")[-1].replace(".tif", "_overlay_w_circ.tif")), image_with_circles)
    
    
if __name__ == "__main__":
    # Example usage
    image_path = r"D:\Code\Codebase_Bha\Dev_Project22_QRCode_reader_coordnates_extraction\SCANS\test_good\S700F99T99REG.tif"  # Path to your image file
    outputPath = os.path.join("\\".join(image_path.split("\\")[:-1]), "out")
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)
    # TESTING
    generate_masks(image_path, outputPath)
