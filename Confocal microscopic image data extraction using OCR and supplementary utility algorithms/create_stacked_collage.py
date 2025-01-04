
import cv2
import os
from typing import Tuple

def resize_img(dest_img_dimensions: Tuple[int, int], name_of_img_to_be_resized: str) -> np.ndarray:
    """
    Resizes an image to the specified dimensions.

    Args:
        dest_img_dimensions (Tuple[int, int]): The target dimensions (width, height) for the resized image.
        name_of_img_to_be_resized (str): The path to the image file to be resized.

    Returns:
        np.ndarray: The resized image.
    """
    img = cv2.imread(name_of_img_to_be_resized)
    print(img.shape, name_of_img_to_be_resized.split("\\")[-1])
    resized_img = cv2.resize(img, dest_img_dimensions)
    return resized_img


    
def transform_imgs_into_standard_dimensions(dims: Tuple[int, int], inpath: str, *args: str) -> Tuple[np.ndarray, ...]:
    """
    Resizes multiple images to standard dimensions and returns them as a tuple.

    Args:
        dims (Tuple[int, int]): The target dimensions (width, height) for the resized images.
        inpath (str): The directory path where the images are located.
        *args (str): Variable length argument list of image file names to be resized.

    Returns:
        Tuple[np.ndarray, ...]: A tuple containing the resized images.
    """
    list_imgs = []
    for imgname in args:
        imgname = os.path.join(inpath, imgname)
        list_imgs.append(resize_img(dims, imgname))

    return tuple(list_imgs)


def main() -> None:
    """
    Main function to resize and concatenate specific images from a directory.

    The function reads images from a specified directory, resizes them to standard dimensions,
    concatenates them horizontally, and saves the resulting image.
    """
    PATH_IN = r"path_to_images"
    DIMS = (1000, 1000)
    blue_img_orig_name = [img for img in os.listdir(PATH_IN) if "blue" in img][0]
    mosaic_block_img_conv_name = [img for img in os.listdir(PATH_IN) if "VivaBlock" in img][0]
    macro_img_orig_name = [img for img in os.listdir(PATH_IN) if "macro" in img][0]
    super_imposed_thresh_img_name = [img for img in os.listdir(PATH_IN) if "thresh" in img][0]

    PATH_OUT = os.path.join(PATH_IN, "main_out2")
    if not os.path.isdir(PATH_OUT):
        os.mkdir(PATH_OUT)

    blue_img_orig, macro_img_orig, super_imposed_thresh_img, mosaic_block_img_conv = transform_imgs_into_standard_dimensions(
        DIMS, PATH_IN, blue_img_orig_name, mosaic_block_img_conv_name, macro_img_orig_name, super_imposed_thresh_img_name
    )

    stack_final = cv2.hconcat([blue_img_orig, macro_img_orig, super_imposed_thresh_img, mosaic_block_img_conv])

    # Save the concatenated image
    cv2.imwrite(os.path.join(PATH_OUT, "concatenated_stack.jpg"), stack_final)

if __name__ == "__main__":
    main()
