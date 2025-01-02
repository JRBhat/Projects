import cv2
from pyzbar.pyzbar import decode
import json
import numpy as np
import os
import shutil
import logging
from typing import List, Dict, Tuple, Optional


def preprocess_image(img_path: str, testing: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Preprocess the input image by converting to grayscale, applying Gaussian blur, 
    and performing Otsu's thresholding.

    Args:
        img_path (str): Path to the input image.
        testing (bool): If True, display intermediate images for debugging (default is False).

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: The original image, processed image after thresholding, and the grayscale image.
    """
    image = cv2.imread(img_path)
    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    closed = fill_holes(thresh)
    cv2.imwrite(f'ROI_Test.png', closed)
    if testing:
        cv2.imshow('ROI', closed)
        cv2.waitKey()
    return original, closed, image


def fill_holes(thresh: np.ndarray) -> np.ndarray:
    """
    Apply morphological closing to fill small holes in the foreground objects of a binary image.

    Args:
        thresh (np.ndarray): The binary thresholded image.

    Returns:
        np.ndarray: The image with filled holes.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed_img = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=5)
    return closed_img


def get_qr_code_coords(closed_img: np.ndarray, image: np.ndarray, original: np.ndarray, padding: int = 55, testing: bool = False) -> List[Dict]:
    """
    Detect potential QR code regions in the image by finding contours and filtering them based on shape, area, and aspect ratio.

    Args:
        closed_img (np.ndarray): The binary image after thresholding and morphological operations.
        image (np.ndarray): The original color image.
        original (np.ndarray): The original image for decoding purposes.
        padding (int): Padding added to the bounding box around QR code regions (default is 55).
        testing (bool): If True, display the detected ROIs for debugging (default is False).

    Returns:
        List[Dict]: A list of dictionaries containing the coordinates and decoded data of detected QR codes.
    """
    cnts = cv2.findContours(closed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    
    final_coords = []
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        x, y, w, h = get_padded_bbox(approx, padding)
        area = cv2.contourArea(c)
        ar = w / float(h)
        ROI = image[y:y + h, x:x + w]
        
        if testing:
            try:
                cv2.imshow('ROI', ROI)
                cv2.waitKey()
            except:
                pass
        
        if area > 25000 and (w and h) > 150 and (w and h) < 300:
            data = decode(original[y:y + h, x:x + w])
            if len(data) == 0:
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                test_img = cv2.morphologyEx(original, cv2.MORPH_CLOSE, kernel, iterations=1)
                if testing:
                    cv2.imshow('ROI', test_img[y:y + h, x:x + w])
                    cv2.waitKey()
                data = decode(test_img[y:y + h, x:x + w])

            final_coords.append({"sum": x + y, "x": x, "y": y, "width": w, "height": h, "data": str(data[0][0])[1:].replace("'", "")})
            
            if testing:
                cv2.imwrite(f'ROI_{len(final_coords)}.png', ROI)
    
    if len(final_coords) == 4:
        return sorted(final_coords, key=lambda x: x["sum"])
    else:
        logging.error("Coords mismatch <4")
        return sorted(final_coords, key=lambda x: x["sum"])


def get_padded_bbox(approx: np.ndarray, padding: int) -> Tuple[int, int, int, int]:
    """
    Expands the bounding box of the detected QR code region to ensure it fully encompasses the QR code.

    Args:
        approx (np.ndarray): The polygon approximation of the contour.
        padding (int): Padding added to the bounding box.

    Returns:
        Tuple[int, int, int, int]: The padded bounding box coordinates (x, y, w, h).
    """
    x, y, w, h = cv2.boundingRect(approx)
    x = x - padding
    y = y - padding
    w = w + 2 * padding
    h = h + 2 * padding
    return x, y, w, h


def update_ptx_with_new_coords(coords_list: List[Dict], path: str, dummy_ptx_path: str) -> None:
    """
    Updates the PTX file with the new coordinates corresponding to the detected QR codes.

    Args:
        coords_list (List[Dict]): List of detected QR code coordinates.
        path (str): The path to the image.
        dummy_ptx_path (str): The path to the dummy PTX file.
    """
    data = read_ptx_file(dummy_ptx_path)
    fn = path.split("\\")[-1]
    new_path = dummy_ptx_path.replace("dummy", fn.replace(".tif", ""))
    skw_ptx_path = write_ptx_file(new_path, coords_list, data)
    new_loc_skw_ptx = os.path.join("\\".join(path.split("\\")[:-1]), skw_ptx_path.split("\\")[-1])
    shutil.move(skw_ptx_path, new_loc_skw_ptx)


def write_ptx_file(new_file_path: str, coords_list: List[Dict], data: List[Dict]) -> str:
    """
    Writes the updated coordinates to the PTX file.

    Args:
        new_file_path (str): The path to save the updated PTX file.
        coords_list (List[Dict]): List of detected QR code coordinates.
        data (List[Dict]): Data extracted from the original PTX file.

    Returns:
        str: The path of the new PTX file.
    """
    for item in data:
        if item["id"] == 1:
            item["contour"] = [[ele["x"] + ele["width"] // 2, ele["y"] + ele["height"] // 2] for ele in coords_list]

    with open(new_file_path, "w") as fptx:
        json.dump(data, fptx, indent=4)
    return new_file_path


def read_ptx_file(file_path: str) -> List[Dict]:
    """
    Extracts the data from the PTX file.

    Args:
        file_path (str): Path to the PTX file.

    Returns:
        List[Dict]: Data extracted from the PTX file.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def extract_coordinates(data: List[Dict]) -> Dict[str, np.ndarray]:
    """
    Extracts coordinates of QR codes and other objects from PTX data.

    Args:
        data (List[Dict]): PTX data containing contours.

    Returns:
        Dict[str, np.ndarray]: A dictionary with arrays of extracted coordinates for QR codes and circles.
    """
    arr_dict = {}
    for item in data:
        if item['id'] == 1:
            arr_dict["qrcoords"] = np.array(item['contour'])
        elif item["id"] == 2:
            arr_dict["top_circles"] = np.array(item['contour'])
        elif item["id"] == 3:
            arr_dict["bottom_circles"] = np.array(item['contour'])
        else:
            id = item["id"]
            raise ValueError(f"No object with id == {id} found in the PTX file")
    return arr_dict


def rename_file_to_standard_barcode(scanned_img_path: str, qrcode_coords_data_dict: Dict, n: int) -> Optional[str]:
    """
    Renames the scanned image based on the QR code data.

    Args:
        scanned_img_path (str): Path to the scanned image.
        qrcode_coords_data_dict (Dict): The dictionary containing QR code data.
        n (int): The index of the QR code data to use for renaming.

    Returns:
        Optional[str]: The new path of the renamed image, or None if no valid QR code data was found.
    """
    try:
        if "Studie" in qrcode_coords_data_dict[n]["data"]:
            new_fn_path = scanned_img_path.replace(scanned_img_path.split("\\")[-1], qrcode_coords_data_dict[n]["data"][-4:] + "F01T01SKW.tif")
            os.rename(scanned_img_path, new_fn_path)
            return new_fn_path
        else:
            logging.warning("Possible QR code containing Studyno was not read")
            return None
    except TypeError:
        logging.error("Possible Coordinates mismatch")
        return None


def detect_qrcodes_from_skewed_image(path: str, dummy_ptx_path: str, pad: int = 20, test: bool = False) -> Tuple[int, str]:
    """
    Detect QR codes from a skewed image, update the PTX file, and rename the image.

    Args:
        path (str): Path to the input image.
        dummy_ptx_path (str): Path to the dummy PTX file.
        pad (int): Padding for bounding box (default is 20).
        test (bool): If True, display intermediate images for debugging (default is False).

    Returns:
        Tuple[int, str]: Status code and the path of the processed image.
    """
    original, thresh, image = preprocess_image(path, testing=test)
    
    sorted_qrcode_coords = get_qr_code_coords(thresh, image, original, padding=pad, testing=test)
    new_path = rename_file_to_standard_barcode(path, sorted_qrcode_coords, 0)
    
    if new_path == None:
        for num, _ in enumerate(sorted_qrcode_coords):
            new_path = rename_file_to_standard_barcode(path, sorted_qrcode_coords, num)
            if new_path != None:
                break
    
    if new_path != None:
        path = new_path
    
    if len(sorted_qrcode_coords) == 4 and int(sorted_qrcode_coords[0]["width"]) < 200:
        log_path = "\\".join(path.split("\\")[:-1])
        with open(os.path.join(log_path, "images_inverted.log"), "a+") as logf:
            logf.writelines(f"{path}\n")
        return 1, path
    
    if len(sorted_qrcode_coords) != 4:
        for _ in range(6):
            closed_img = fill_holes(thresh)
            sorted_qrcode_coords = get_qr_code_coords(closed_img, image, original, padding=pad, testing=test)
            if len(sorted_qrcode_coords) == 4:
                break
        return 2, path
    else:
        update_ptx_with_new_coords(sorted_qrcode_coords, path, dummy_ptx_path)
        return 0, path


def main():
    pass


if __name__ == "__main__":
    main()
