import numpy as np
import matplotlib.pyplot as plt
from skimage import io, color, feature, transform, draw
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.feature import canny
from skimage.draw import circle_perimeter
from scipy import ndimage as ndi
import cv2
from typing import Tuple, List


def detect_circles(image: np.ndarray, min_radius: int = 256, max_radius: int = 256, min_distance: int = 999) -> Tuple[List[int], List[int], List[int]]:
    """
    Detects circles in the given image using the Hough Transform method.

    Args:
        image (np.ndarray): The input image (grayscale or RGB).
        min_radius (int): The minimum radius of the circles to detect (default is 256).
        max_radius (int): The maximum radius of the circles to detect (default is 256).
        min_distance (int): The minimum distance between detected centers (default is 999).

    Returns:
        Tuple[List[int], List[int], List[int]]: The x-coordinates, y-coordinates, and radii of detected circles.
    """
    # Convert to grayscale if necessary
    if image.ndim == 3:
        gray_image = color.rgb2gray(image)
    else:
        gray_image = image

    # Apply Gaussian blur to reduce noise
    blurred = ndi.gaussian_filter(gray_image, sigma=2)

    # Edge detection with lower threshold for dotted circles
    edges = feature.canny(blurred, sigma=1, low_threshold=0, high_threshold=0)

    # Dilate edges to connect nearby dots
    dilated_edges = ndi.binary_dilation(edges)

    # Detect circles using Hough Transform
    hough_radii = np.arange(min_radius, max_radius, 1)
    hough_res = transform.hough_circle(dilated_edges, hough_radii)

    # Select circles from the Hough Transform results
    accums, cx, cy, radii = transform.hough_circle_peaks(
        hough_res, hough_radii,
        total_num_peaks=24,
        min_xdistance=min_distance,
        min_ydistance=min_distance
    )
    return cx, cy, radii


# Load the image
image_path = r"D:\Code\Codebase_Bha\Dev_Project22_QRCode_reader_coordnates_extraction\PIAS\S000F00T00VAL.tiff"
image = io.imread(image_path)

# Check if the image has 4 channels (RGBA) and convert to RGB if necessary
if image.shape[-1] == 4:
    image = color.rgba2rgb(image)

# Detect circles
cx, cy, radii = detect_circles(image)

# Visualize results
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(image, cmap=plt.cm.gray)

for center_y, center_x, radius in zip(cy, cx, radii):
    # Draw circle perimeter
    circy, circx = draw.circle_perimeter(center_y, center_x, radius, shape=image.shape)
    ax.plot(circx, circy, 'r-')
    
    # Print center coordinates
    print(f"Circle center: ({center_x}, {center_y})")
    
    # Add text annotation on the image
    ax.text(center_x, center_y, f'({center_x}, {center_y})', 
            color='white', fontsize=8, ha='center', va='center')

plt.tight_layout()
plt.show()
