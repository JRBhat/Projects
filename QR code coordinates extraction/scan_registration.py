# get the qr code top-left corner coordinates from baseline ptx

# read every scanned image and obtain the qr code top-left corner coordinates - ignore the BIG qr code point. Only the small ones

# Apply similarity/Eucleadian transform - pass the src (baseline coords) and destination (scanned image coords) to the object
# https://scikit-image.org/docs/stable/api/skimage.transform.html#skimage.transform.AffineTransform
# https://scikit-image.org/docs/stable/api/skimage.transform.html#skimage.transform.EuclideanTransform
####TUTORIAL###
# https://scikit-image.org/docs/stable/auto_examples/transform/plot_geometric.html#sphx-glr-auto-examples-transform-plot-geometric-py
# https://scikit-image.org/docs/stable/auto_examples/transform/plot_transform_types.html#sphx-glr-auto-examples-transform-plot-transform-types-py

# if using .inverse(dst) then pass the circles coords as dst (to be checked if needed or not) 

import json
import numpy as np
from skimage import io, transform
import shutil
import logging
from detect_qrcode import read_ptx_file, write_ptx_file, extract_coordinates


def register_image(reference_ptx: str, skewed_ptx: str, skewed_image_path: str) -> tuple:
    """
    Registers a skewed image using a reference PTX file and skewed PTX file by calculating a similarity transformation.
    
    :param reference_ptx: Path to the reference PTX file.
    :type reference_ptx: str
    :param skewed_ptx: Path to the skewed PTX file.
    :type skewed_ptx: str
    :param skewed_image_path: Path to the skewed image.
    :type skewed_image_path: str
    :return: A tuple containing transformed coordinates and the transformation matrix.
    :rtype: tuple
    """
    # Read PTX files
    ref_data = read_ptx_file(reference_ptx)
    skewed_data = read_ptx_file(skewed_ptx)

    # Extract coordinates
    ref_coords_dict = extract_coordinates(ref_data)
    skewed_coords_dict = extract_coordinates(skewed_data)

    # Ensure we have at least 3 pairs of coordinates
    try:
        assert len(ref_coords_dict) >= 3 and len(skewed_coords_dict) >= 3, "Expected at least 3 pairs of coordinates"
    except AssertionError:
        logging.error(f"{skewed_image_path} Fails.\n\n Expected at least 3 pairs of coordinates")
        transformed_coords, tform = None, None
        return transformed_coords, tform

    # Compute the similarity transform
    try:
        tform = transform.SimilarityTransform()
        # Estimate the transformation function from src:org ref qrcode to dst: skw qrcode coordinate
        tform.estimate(ref_coords_dict["qrcoords"], skewed_coords_dict["qrcoords"])
        
    except ValueError:
        logging.error(f"{skewed_image_path} fails due to coords dimension mismatch")
        transformed_coords, tform = None, None
        return transformed_coords, tform
         
    # Get the transformed coordinates
    transformed_qrcodes = tform(ref_coords_dict["qrcoords"])
    transformed_top_circles = tform(ref_coords_dict["top_circles"])
    transformed_bottom_circles = tform(ref_coords_dict["bottom_circles"])
    
    transformation_dict = {
        "ptx_id1": transformed_qrcodes,
        "ptx_id2": transformed_top_circles,
        "ptx_id3": transformed_bottom_circles
    }
    
    return transformation_dict, tform


def registration_step(reference_ptx: str, skewed_ptx: str, skewed_image_path: str, 
                      registered_img_savepath: str, print_reg_details: bool = False) -> None:
    """
    Registers the skewed image using the reference PTX and skewed PTX files, applies the transformation,
    and saves the registered PTX file.
    
    :param reference_ptx: Path to the reference PTX file.
    :type reference_ptx: str
    :param skewed_ptx: Path to the skewed PTX file.
    :type skewed_ptx: str
    :param skewed_image_path: Path to the skewed image.
    :type skewed_image_path: str
    :param registered_img_savepath: Path to save the registered image.
    :type registered_img_savepath: str
    :param print_reg_details: Whether to print registration details (default is False).
    :type print_reg_details: bool
    :return: None
    """
    transformed_coords_dict, transformation_matrix = register_image(reference_ptx, skewed_ptx, skewed_image_path)
    
    create_final_ptx(skewed_ptx, transformed_coords_dict)


def create_final_ptx(skewed_ptx_path: str, transformed_coords_dict: dict) -> str:
    """
    Creates a final PTX file by saving the transformed coordinates into the skewed PTX file.
    
    :param skewed_ptx_path: Path to the skewed PTX file.
    :type skewed_ptx_path: str
    :param transformed_coords_dict: Dictionary containing transformed coordinates.
    :type transformed_coords_dict: dict
    :return: Path to the updated PTX file.
    :rtype: str
    """
    src_path = skewed_ptx_path
    dest_path = skewed_ptx_path.replace("SKW", "SKW_BCKP")
    shutil.copy(src_path, dest_path)
    
    data = read_ptx_file(skewed_ptx_path)
        
    for item in data:
        if item["id"] == 1:
            item["contour"] = np.ndarray.tolist(transformed_coords_dict["ptx_id1"])
        elif item["id"] == 2:
            item["contour"] = np.ndarray.tolist(transformed_coords_dict["ptx_id2"])
        elif item["id"] == 3:
            item["contour"] = np.ndarray.tolist(transformed_coords_dict["ptx_id3"])            

    with open(skewed_ptx_path, "w") as fptx:
        json.dump(data, fptx, indent=4)
        
    return skewed_ptx_path


def main() -> None:
    """
    Main function that demonstrates how to use the registration step by passing PTX file paths and skewed image path.
    
    :return: None
    """
    # Usage example
    reference_ptx = r"path_to_reference_ptx\S998F99T99ORG.ptx"
    skewed_ptx = r"path_to_skewed_ptx\S987F99T99SKW.ptx"
    skewed_image_path = r"path_to_skewed_img\S901F01T01SKW.tif"
    registered_img_savepath = r"path_to_registered_skew_image\S901F01T01REG.tif"
    
    registration_step(reference_ptx, skewed_ptx, skewed_image_path, registered_img_savepath, print_reg_details=True)


if __name__ == "__main__":
    main()
