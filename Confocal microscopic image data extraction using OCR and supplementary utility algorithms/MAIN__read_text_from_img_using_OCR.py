import cv2
import pytesseract
import re
from matplotlib import pyplot as plt
import os
import pickle
import numpy as np
import math
from time import sleep
from Util import readData, getAllFiles
from ImageAnalysis import writeImage, readRGBImage
from typing import Dict, Tuple

# download and install if necessary ; and assign path to tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"local_path_to_tessaract_install\Tesseract-OCR\tesseract.exe"


#1 OCR finding coordinates..................................


def create_img_coord_dict(imagepath: str) -> Tuple[Dict[str, np.ndarray], np.ndarray]:
    """
    Specifies the image slice that corresponds to the text of interest.

    Args:
        imagepath (str): The file path to the image.

    Returns:
        Tuple[Dict[str, np.ndarray], np.ndarray]: A dictionary mapping text labels to their corresponding image slices and the original image.
    """
    image = cv2.imread(imagepath)

    text_dict = {
        "filename": image[1000:1000+22, 0:0+180],
        "x": image[1019:1019+25, 0:600],
        "y": image[1019:1019+25, 0:600]
    }

    return text_dict, image

def get_text_from_crp_img(crp_img: np.ndarray) -> str:
    """
    Retrieves text, symbols, and digits from a cropped image slice using Tesseract OCR.

    Args:
        crp_img (np.ndarray): The cropped image slice.

    Returns:
        str: The extracted text, symbols, and numbers in string format.
    """
    gray_image = cv2.cvtColor(crp_img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding
    threshold_image = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY_INV)[1]

    plt.imshow(threshold_image)

    # Apply OCR
    text = pytesseract.image_to_string(gray_image)

    return text

def extract_text_from_img_coords(img_path: str) -> Tuple[str, str, str]:
    """
    Extracts text from an image using OCR and processes the output to retrieve specific information.

    Args:
        img_path (str): The file path to the image.

    Returns:
        Tuple[str, str, str]: The extracted filename, x-coordinate, and y-coordinate.
    """
    filename_regx = r"v[0-9]*.bmp"

    img_coords_dict, img = create_img_coord_dict(img_path)

    extracted_text_dict = {}
    for k, v in img_coords_dict.items():
        text = get_text_from_crp_img(v)
        extracted_text_dict[k] = str(text)

    print(extracted_text_dict)

    filename = re.search(filename_regx, extracted_text_dict["filename"]).group(0)
    x_coord = re.findall(r'[-+]?\d*\.\d+', extracted_text_dict["x"])[0]
    imgx = np.array(img[1029:1029+3, 21:21+1])

    # Count the number of black pixels in the image
    num_black_pixels_x = np.count_nonzero(imgx == 0)

    if x_coord[0] != "-" and num_black_pixels_x == 3:
        x_coord = "-" + x_coord

    y_coord = re.findall(r'[-+]?\d*\.\d+', extracted_text_dict["y"])[1]
    imgy = np.array(img[1029:1029+3, 105:105+1])

    # Count the number of black pixels in the image
    num_black_pixels_y = np.count_nonzero(imgy == 0)

    if y_coord[0] != "-" and num_black_pixels_y == 3:
        y_coord = "-" + y_coord

    print(num_black_pixels_x, num_black_pixels_y)
    print(filename, x_coord, y_coord)

    return filename, x_coord, y_coord

def create_pickled_dict_containing_stacks_and_blocks_per_subject(inpath: str, outpath_pickle: str) -> None:
    """
    Creates a pickled dictionary containing stacks and blocks per subject.

    Args:
        inpath (str): The input directory path.
        outpath_pickle (str): The output path for the pickled dictionary.
    """
    subj_dict = {}
    for root, dirs, _ in os.walk(inpath):
        if len(dirs) != 0:
            subj_no = None
            Block_dict = {}
            Stack_dict = {}
            for dirname in dirs:
                if "VivaBlock" in dirname:
                    subj_no = re.search(r"S[0-9]{2}", root).group(0)
                    folderpath = os.path.join(root, dirname)
                    img_tup_list_temp = []
                    for imgname in os.listdir(folderpath):
                        if imgname[0] == "v" and "#" not in imgname:
                            fn, x, y = extract_text_from_img_coords(os.path.join(folderpath, imgname))
                            img_tup_list_temp.append((x, y, os.path.join(folderpath, fn)))
                    Block_dict[dirname] = img_tup_list_temp

                elif "VivaStack" in dirname:
                    subj_no = re.search(r"S[0-9]{2}", root).group(0)
                    folderpath = os.path.join(root, dirname)
                    for imgname in os.listdir(folderpath):
                        if imgname == "v0000000.bmp":
                            fn, x, y = extract_text_from_img_coords(os.path.join(os.path.join(root, dirname), imgname))
                    Stack_dict[dirname] = (x, y, os.path.join(folderpath, fn))

            if subj_no is not None and "S" in subj_no:
                subj_dict[subj_no] = [Stack_dict, Block_dict]

    with open(outpath_pickle, "wb") as f:
        pickle.dump(subj_dict, f)



#2 marking block images according to closest stacks..................................
def mark_block_images_according_to_stack_coordinates(inpath: str, main_dict_path: str) -> None:
    """
    Marks block images according to the closest stack coordinates.

    Args:
        inpath (str): The input directory path.
        main_dict_path (str): The path to the main dictionary.
    """
    main_dict = readData(main_dict_path)

    for subj in main_dict.keys():
        for block_name, v in main_dict[subj][1].items():
            block_path = [r for r, _, _ in os.walk(inpath) if subj in r and block_name in r][0]

            block_coordinates = [(float(x[0]), float(x[1])) for x in main_dict[subj][1][block_name]]
            for stack_name, v in main_dict[subj][0].items():
                target = (float(v[0]), float(v[1]))
                print(stack_name, min(enumerate(block_coordinates), key=lambda point: math.hypot(target[1]-point[1][1], target[0]-point[1][0])))

                best_image_data = min(enumerate(block_coordinates), key=lambda point: math.hypot(target[1]-point[1][1], target[0]-point[1][0]))

                target_image = os.path.join(block_path, "v0000%03d.bmp" % best_image_data[0])

                arr = cv2.imread(target_image)

                out_array = np.dstack([arr, arr, arr])
                arr[:, :, 0] = 0
                arr[:, :, 1] = 0

                # Annotation parameters
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = int(max(arr.shape[0], arr.shape[1]) / 50)
                thickness = 50
                color = (255, 255, 255)

                # Add annotation
                channel_annotated = cv2.cvtColor(arr[:, :, 0], cv2.COLOR_GRAY2BGR)
                annotation = stack_name.split("#")[-1]
                text_size, _ = cv2.getTextSize(annotation, font, font_scale, thickness)
                text_x = int((arr.shape[1] - text_size[0]) / 2)
                text_y = int((arr.shape[0] + text_size[1]) / 2)
                cv2.putText(channel_annotated, annotation, (text_x, text_y), font, font_scale, color, thickness)
                merged = arr.copy()
                merged[:, :, 0] = channel_annotated[:, :, 0]
                cv2.imwrite(target_image, merged)


#3 creating the mosaic from marked block images...................................

def create_mosaic_from_marked_stacks(inpath: str, main_dict_path: str) -> None:
    """
    Creates a mosaic from marked block images.

    Args:
        inpath (str): The input directory path.
        main_dict_path (str): The path to the main dictionary.
    """
    main_dict = readData(main_dict_path)

    for subj in main_dict.keys():
        for block_name, _ in main_dict[subj][1].items():
            block_path = [r for r, _, _ in os.walk(inpath) if subj in r and block_name in r][0]
            block_name = block_name.replace(" #", "")
            mosaic_name = f"{subj}_F1_T2_{block_name}.png"
            out_path = os.path.join(block_path, mosaic_name)

            mosaik_files = sorted(getAllFiles(block_path, "v000*.bmp", depth=0))
            steps = 12

            def prepare_image(imagename: str) -> np.ndarray:
                im1 = readRGBImage(imagename)
                return im1[:im1.shape[1], :im1.shape[1], :]

            im_out = []
            for rg in range(3):
                mosaik_in_images = [[
                    [prepare_image(x)[:, :, rg] for x in mosaik_files[row*steps: (row+1)*steps][::-1]],
                    [prepare_image(x)[:, :, rg] for x in mosaik_files[row*steps: (row+1)*steps]]
                ][row % 2] for row in range(steps)]

                im_out.append(np.block(mosaik_in_images))

            writeImage(np.dstack(im_out).astype(np.uint8), out_path)
      

def main() -> None:
    """
    Main function to process images, create pickled dictionaries, mark block images, and create mosaics.
    """
    PATH = r"path_to_images"
    OUTPATH = os.path.join(r"path_to_images\data", PATH.split("\\")[-1] + "_pickled_dict.pkl")

    create_pickled_dict_containing_stacks_and_blocks_per_subject(PATH, OUTPATH)
    # sleep(5)
    # mark_block_images_according_to_stack_coordinates(PATH, OUTPATH)
    # sleep(5)
    # create_mosaic_from_marked_stacks(PATH, OUTPATH)

if __name__ == "__main__":
    main()


