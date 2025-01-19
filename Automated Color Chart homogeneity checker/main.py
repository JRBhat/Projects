import cv2
import numpy as np
import pprint
import matplotlib.pyplot as plt
import os

from LAB_Extractor import extract_lab

# Specify ROI mask dimensions and apply mask over the image
color_chart_coord_dict = {
    "white": (2750, 4792, 100, 100)
}

def create_roi_mask(img: np.ndarray, coords: tuple[int, int, int, int]) -> np.ndarray:
    """
    Create a binary mask for a specified region of interest (ROI).

    Args:
        img (np.ndarray): Input image.
        coords (tuple[int, int, int, int]): ROI coordinates as (x, y, width, height).

    Returns:
        np.ndarray: Mask with the ROI set to 1 and the rest set to 0.
    """
    x, y, w, h = coords
    mask = np.zeros_like(img, dtype=img.dtype)
    mask[y:y+h, x:x+w] = 1
    return mask

def draw_rect(masked_img: np.ndarray, color_coords: tuple[int, int, int, int], 
              l_val: float, thresh: dict[str, int]) -> np.ndarray:
    """
    Draw a rectangle around the specified ROI with a color indicating luminance tolerance.

    Args:
        masked_img (np.ndarray): Image on which to draw the rectangle.
        color_coords (tuple[int, int, int, int]): ROI coordinates as (x, y, width, height).
        l_val (float): Median luminance value.
        thresh (dict[str, int]): Dictionary containing tolerance thresholds.

    Returns:
        np.ndarray: Image with the rectangle drawn on it.
    """
    if l_val < thresh["medium_tolerance"]:
        color = (0, 255, 255)  # yellow
        thickness = 4
    elif l_val < thresh["max_tolerance"]:
        color = (0, 0, 255)  # red
        thickness = 7
    else:
        color = (0, 255, 0)  # green
        thickness = 1

    x, y, w, h = color_coords
    return cv2.rectangle(masked_img, (x, y), (x + w, y + h), color, thickness)

def save_masked_img(Img: np.ndarray, mask: np.ndarray, coords: tuple[int, int, int, int], 
                    colorname: str, mask_path: str, fn: str, l_val: float, 
                    thresh: dict[str, int]) -> None:
    """
    Save an annotated image with a mask and bounding rectangle applied.

    Args:
        Img (np.ndarray): Original image.
        mask (np.ndarray): Mask for the ROI.
        coords (tuple[int, int, int, int]): ROI coordinates as (x, y, width, height).
        colorname (str): Name of the color associated with the ROI.
        mask_path (str): Path to save the masked image.
        fn (str): Filename of the original image.
        l_val (float): Median luminance value.
        thresh (dict[str, int]): Dictionary containing tolerance thresholds.
    """
    if not os.path.exists(mask_path):
        os.mkdir(mask_path)

    masked_fn = fn.replace(".tif", f"{colorname}_masked.png")
    full_mask = mask[:, :, 0]
    full_image_with_circle = draw_rect(Img, coords, l_val, thresh)
    full_image_with_circle = np.dstack([full_image_with_circle, 100 + 60 * full_mask])
    full_image_with_circle[:, :, 3][full_mask == 1] = 255

    annotated_crpd_img_with_circle_and_transparency = annotate_img(
        full_image_with_circle[
            coords[1]-300 : (coords[1]-300) + coords[3]+600,
            coords[0]-300 : (coords[0]-300) + coords[2]+600, :
        ],
        l_val, thresh, color=(150, 150, 150)
    )

    cv2.imwrite(os.path.join(mask_path, masked_fn), annotated_crpd_img_with_circle_and_transparency)

def annotate_img(cropped_image_with_circle: np.ndarray, l_val: float, 
                 thresh: dict[str, int], color: tuple[int, int, int] = (255, 255, 255)) -> np.ndarray:
    """
    Add annotation text to the image indicating luminance value.

    Args:
        cropped_image_with_circle (np.ndarray): Cropped image with ROI highlighted.
        l_val (float): Median luminance value.
        thresh (dict[str, int]): Dictionary containing tolerance thresholds.
        color (tuple[int, int, int]): Color of the text annotation (default is white).

    Returns:
        np.ndarray: Annotated image.
    """
    text = f"l_median: {l_val}" 
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    text_x = (cropped_image_with_circle.shape[1] - text_size[0]) // 2
    text_y = cropped_image_with_circle.shape[0] - 50
    thickness = 2

    if l_val < thresh["medium_tolerance"]:
        color = (0, 0, 0)  # black
        thickness = 2
    elif l_val < thresh["max_tolerance"]:
        color = (0, 0, 255)  # red
        thickness = 4

    cv2.putText(
        img=cropped_image_with_circle, text=text,
        org=(text_x, text_y), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1, color=color, thickness=thickness
    )
    return cropped_image_with_circle

def main() -> None:
    """
    Main function to process images, generate masks, and plot luminance trends.
    """
    BASEPATH = r"D:\STUDIES\23.0264-99_Perrigo_Klifo_studie\DATA\STUDY_DATA\finalised"
    MASKPATH = os.path.join(BASEPATH, "masks_white_colorchart")
    SAVE_MASKS_FLAG = False
    THRESHOLD = {"max_tolerance": 90, "medium_tolerance": 93}

    img_color_dict = {}

    for fn in sorted(os.listdir(BASEPATH)):
        if fn.endswith(("tif", "TIF", "jpg", "JPG")):
            colors_dict = {}
            for colorname, coords in color_chart_coord_dict.items():
                Img = cv2.imread(os.path.join(BASEPATH, fn))
                if "T02" in fn and fn[2:4] not in [str(i) for i in range(12, 56)]:
                    coords = (2750, 4892, 100, 100)
                mask = create_roi_mask(Img, coords)
                lab_arr = extract_lab(Img[:, :, ::-1], convert=False)
                l_val = np.median(lab_arr[:, :, 0][mask[:, :, 0] == 1])
                colors_dict[colorname] = (fn, l_val)
                if SAVE_MASKS_FLAG:
                    save_masked_img(Img, mask, coords, colorname, MASKPATH, fn, l_val, THRESHOLD)
            img_color_dict[fn] = colors_dict

    x_axis_range = list(img_color_dict.keys())
    y1_axis_range = [v["white"][1] for v in img_color_dict.values()]

    plt.plot(x_axis_range, y1_axis_range)
    plt.xticks(rotation=93)
    plt.show()
    input("Press enter to end....")

if __name__ == "__main__":
    main()
