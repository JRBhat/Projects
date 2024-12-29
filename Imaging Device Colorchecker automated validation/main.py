import cv2
import numpy as np
import pprint
import matplotlib.pyplot as plt
from typing import Dict, Tuple


# Path to image files
path_std2 = r"path to 06_T01_Front View_Standard 2.tif"
path_std1 = r"path to 06_T01_Front View_Standard 1.tif"
path_xpol = r"path to 06_T01_Front View_Cross-Polarized.tif"
path_ppol = r"path to 06_T01_Front View_Parallel-Polarized.tif"

paths = [path_std2, path_std1, path_xpol, path_ppol]

# ROI coordinates for each color patch in the color chart
color_chart_coord_dict: Dict[str, Tuple[int, int, int, int]] = {
    "dark_skin": (712, 4960, 80, 80),
    "light_skin": (842, 4960, 80, 80),
    "blue_sky": (972, 4960, 80, 80),
    "foliage": (1102, 4960, 80, 80),
    "blue_flower": (1232, 4960, 80, 80),
    "bluish_green": (1362, 4960, 80, 80),
    "orange": (2270, 4960, 80, 80),
    "purplish_blue": (2400, 4960, 80, 80),
    "moderate_red": (2530, 4960, 80, 80),
    "purple": (2660, 4960, 80, 80),
    "yellow_green": (2790, 4960, 80, 80),
    "orange_yellow": (2920, 4960, 80, 80),
    "blue": (710, 5090, 80, 80),
    "green": (840, 5090, 80, 80),
    "red": (970, 5090, 80, 80),
    "yellow": (1100, 5090, 80, 80),
    "magenta": (1230, 5090, 80, 80),
    "cyan": (1360, 5090, 80, 80),
    "white": (1492, 4960, 80, 80),
    "neutral_8": (1622, 4960, 80, 80),
    "neutral_6.5": (1752, 4960, 80, 80),
    "neutral_5": (1882, 4960, 80, 80),
    "neutral_3.5": (2009, 4960, 80, 80),
    "black": (2140, 4960, 80, 80),
    "long_grey_patch": (330, 5235, 3035, 50),
}

# Standard color values to compare against (L*, A*, B*)
color_check_standard_dict: Dict[str, Tuple[int, int, int]] = {
    "dark_skin": (38, 12, 14),
    "light_skin": (66, 13, 17),
    "blue_sky": (51, 0, -22),
    "foliage": (43, -17, 22),
    "blue_flower": (56, 13, -25),
    "bluish_green": (72, -31, 1),
    "orange": (62, 28, 58),
    "purplish_blue": (41, 18, -43),
    "moderate_red": (52, 43, 15),
    "purple": (31, 26, -23),
    "yellow_green": (72, -28, 59),
    "orange_yellow": (72, 12, 67),
    "blue": (30, 27, -51),
    "green": (55, -41, 34),
    "red": (41, 51, 26),
    "yellow": (81, -4, 79),
    "magenta": (52, 49, -16),
    "cyan": (52, 22, 27),
    "white": (96, 0, 0),
    "neutral_8": (81, 0, 0),
    "neutral_6.5": (67, 0, 0),
    "neutral_5": (52, 0, 0),
    "neutral_3.5": (36, 0, 0),
    "black": (20, 0, 0),
    "long_grey_patch": (0, 0, 0),
}

# Dictionary to store color name mappings for visualization
magbeth_color_dict: Dict[str, str] = {
    "dark_skin": "saddlebrown",
    "light_skin": "peachpuff",
    "blue_sky": "skyblue",
    "foliage": "forestgreen",
    "blue_flower": "mediumpurple",
    "bluish_green": "mediumturquoise",
    "orange": "orange",
    "purplish_blue": "slateblue",
    "moderate_red": "palevioletred",
    "purple": "rebeccapurple",
    "yellow_green": "yellowgreen",
    "orange_yellow": "goldenrod",
    "blue": "navy",
    "green": "limegreen",
    "red": "darkred",
    "yellow": "yellow",
    "magenta": "mediumvioletred",
    "cyan": "darkcyan",
    "white": "lime",
    "neutral_8": "darkgray",
    "neutral_6.5": "gray",
    "neutral_5": "dimgray",
    "neutral_3.5": "lightslategray",
    "black": "black",
    "long_grey_patch": "lightsteelblue",
}

# Dictionaries to store extracted and computed data
gold_std_delta_dict: Dict[str, Tuple[float, float, float]] = {}
img_color_dict: Dict[str, Tuple[float, float, float]] = {}


def extract_roi_mask(img: np.ndarray) -> np.ndarray:
    """
    Extract a region of interest (ROI) from the image based on predefined coordinates.
    
    Args:
        img: The input image to process.
        
    Returns:
        A masked image with the region of interest isolated.
    """
    # Define the ROI coordinates
    x, y, w, h = 250, 4900, 3240, 470

    # Create a mask of zeros with the same size as the image
    mask = np.zeros_like(img)

    # Draw a white rectangle on the mask at the ROI coordinates
    cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)

    # Apply the mask to the image
    return cv2.bitwise_and(img, mask)


def draw_rect(masked_img: np.ndarray, color_tuple: Tuple[int, int, int, int]) -> None:
    """
    Draw a colored rectangle on the masked image at the specified coordinates.
    
    Args:
        masked_img: The image with the masked region.
        color_tuple: Coordinates of the rectangle (x, y, width, height).
    """
    x, y, w, h = color_tuple
    cv2.rectangle(masked_img, (x, y), (x + w, y + h), (253, 32, 171), -1)


def extract_lab(colorname: str, color_tuple: Tuple[int, int, int, int], masked_img: np.ndarray) -> Tuple[float, float, float]:
    """
    Extract the average LAB color values from a given region of interest in the image.
    
    Args:
        colorname: Name of the color patch.
        color_tuple: Coordinates of the color patch (x, y, width, height).
        masked_img: The masked image with the region of interest.
        
    Returns:
        A tuple containing the average L*, A*, and B* values for the extracted ROI.
    """
    x, y, w, h = color_tuple

    # Extract the ROI from the image
    roi = masked_img[y:y + h, x:x + w]

    # Convert the ROI to LAB color space
    lab_roi = cv2.cvtColor(roi.astype("float32") / 255, cv2.COLOR_BGR2LAB)

    # Calculate the mean LAB values for the ROI
    return tuple(cv2.mean(lab_roi)[:3])


def main() -> None:
    """
    Main function to process all images, extract color information, and compute deltas.
    Plots and displays the comparison results.
    """
    for n, path in enumerate(paths, start=1):
        for k, v in color_check_standard_dict.items():
            # Read image
            img = cv2.imread(path)

            # Create a mask of zeros with the same size as the image
            masked_img = extract_roi_mask(img)

            # Extract LAB values from the color chart
            lab_tup = extract_lab(k, color_chart_coord_dict[k], masked_img)
            img_color_dict[k] = lab_tup
            gold_std_delta_dict[k] = tuple(map(lambda a, b: round(a - b, 2), lab_tup, color_check_standard_dict[k]))

            # Plot the results
            plt.plot(n, img_color_dict[k][0], "o", color=magbeth_color_dict[k])

        print(path)
        pprint.pprint(gold_std_delta_dict)
    
    # Show the final plot
    plt.show()


if __name__ == "__main__":
    main()
