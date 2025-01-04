"""
This script applies a binary mask to all images in a specified directory. 
For each image, pixels corresponding to the mask's black areas are set to black, 
while the remaining pixels retain their original values. The processed images 
are saved in an output directory with filenames indicating they are masked.
"""


import cv2
import numpy as np
import os
from typing import Optional

def apply_mask_to_images(
    input_dir: str, 
    mask_path: str, 
    output_dir: str, 
    file_ext: str = ".TIF"
) -> None:
    """
    Applies a binary mask to all images in the input directory and saves the masked images to the output directory.

    :param input_dir: Path to the directory containing input images.
    :type input_dir: str
    :param mask_path: Path to the binary mask image (grayscale).
    :type mask_path: str
    :param output_dir: Path where masked images will be saved.
    :type output_dir: str
    :param file_ext: File extension to filter images (e.g., '.TIF' or '.jpg'). Default is '.TIF'.
    :type file_ext: str
    :raises FileNotFoundError: If the mask file is not found at the specified path.
    :raises ValueError: If an image cannot be loaded.
    :return: None
    :rtype: None
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the mask as grayscale
    mask = cv2.imread(mask_path, 0)
    if mask is None:
        raise FileNotFoundError(f"Mask file not found at: {mask_path}")

    # Iterate through all images in the input directory
    for image_name in os.listdir(input_dir):
        if image_name.endswith(file_ext):
            image_path = os.path.join(input_dir, image_name)
            img = cv2.imread(image_path)

            if img is None:
                raise ValueError(f"Error loading image: {image_path}")

            # Resize mask if its dimensions do not match the image
            if img.shape[:2] != mask.shape:
                mask_resized = cv2.resize(mask, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
            else:
                mask_resized = mask

            # Apply the mask to the image
            masked_image = img.copy()
            masked_image[mask_resized == 0] = 0

            # Save the masked image
            output_image_name = image_name.replace(file_ext, f"_masked{file_ext}")
            output_image_path = os.path.join(output_dir, output_image_name)
            cv2.imwrite(output_image_path, masked_image)

    print(f"Masked images saved to: {output_dir}")
