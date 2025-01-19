import os
from detect_qrcode import detect_qrcodes_from_skewed_image
from scan_registration import registration_step
import logging
import shutil
from create_binary_mask_overlay import generate_masks


def move_files(img_path: str, bad_path: str) -> None:
    """
    Moves the given image and corresponding PTX files to a specified 'bad' folder.

    :param img_path: The path of the image file to be moved.
    :type img_path: str
    :param bad_path: The destination folder path where the files should be moved.
    :type bad_path: str
    :return: None
    """
    img_reg_path = img_path.replace("SKW", "REG")
    ptx_path = img_path.replace(".tif", ".ptx")
    ptx_reg_path = ptx_path.replace("SKW", "REG")

    for p in [img_path, img_reg_path, ptx_path, ptx_reg_path]:
        try:
            shutil.move(p, os.path.join(bad_path, p.split("\\")[-1]))
            logging.debug(f"{p} successfully moved to bad output folder")
        except FileNotFoundError:
            continue


def main(TEST: bool = False) -> None:
    """
    Main function that processes skewed scanned images, detects QR codes, 
    registers images, and generates binary masks based on the images' status.

    :param TEST: Flag to determine if the function should run in test mode (default is False).
    :type TEST: bool
    :return: None
    """
    # Path to skewed scanned images folder
    PATH = r"path_to_scanned_skew_images_renamed"
    
    DUMMY_PTX_PATH = r"path_to_dummy_ptx\dummy.ptx"
    REF_PTX_PATH = r"path_to_reference_validation_ptx\S000F00T00VAL.ptx"
    LOGPATH = os.path.join(PATH, "app.log")
    BAD_PATH = os.path.join(PATH, "bad")
    INV_PATH = os.path.join(PATH, "inverted")
    OUTPATH = os.path.join(PATH, "output")
    
    # initialize logging object and configure it
    logging.basicConfig(
        filename=LOGPATH,
        encoding="utf-8",
        filemode="a",
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        level=logging.DEBUG)
    
    # Reads all skewed images from the folder that contains all the skewed scanned images by looping over it
    for fn in os.listdir(PATH):
        if fn.endswith(".tif"):
            skwd_img_path = os.path.join(PATH, fn)  # SKW.tif
            # detect qr code from each image and create corresponding ptx and update the coords 
            status, new_skwd_img_path = detect_qrcodes_from_skewed_image(skwd_img_path, DUMMY_PTX_PATH, test=TEST)
            skwd_img_path = new_skwd_img_path
            fn = new_skwd_img_path.split("\\")[-1]
            if status == 0:
                # register the skewed image and save new REG image, also copy the ORG.ptx to create a new REG.ptx
                skwd_ptx_path = skwd_img_path.replace(".tif", ".ptx")  # SKW.ptx
                reg_img_save_path = skwd_img_path.replace("SKW", "REG")
                registration_step(REF_PTX_PATH, skwd_ptx_path, skwd_img_path, reg_img_save_path, print_reg_details=TEST)
                logging.debug(f"{fn} successfully registered")
                
            elif status == 1:
                if not os.path.isdir(INV_PATH):
                    os.mkdir(INV_PATH)
                move_files(os.path.join(PATH, fn), INV_PATH)
                logging.warning(f"Inverted image {fn} detected. Skipping for now. Check log file later to make ammends..")
                continue
            else:
                if not os.path.isdir(BAD_PATH):
                    os.mkdir(BAD_PATH)
                move_files(os.path.join(PATH, fn), BAD_PATH)
                logging.error(f"{fn} coordinates < 4")
                continue
            
    for fn in os.listdir(PATH):
        if fn.endswith(".tif") and "SKW" in fn:
            generate_masks(os.path.join(PATH, fn), OUTPATH)
            print(f"generating the masks for {fn}")
            logging.debug(f"masks for {fn} successfully generated")


if __name__ == "__main__":
    main(TEST=False)
