# pip install colour-science

import numpy as np
import colour
import os
import cv2
import itertools
from ImageAnalysis.ColorConversion import sRGB_to_lab
from ImageAnalysis.ImageIO import readImage
from typing import Union, List, Any


def extract_lab_validation(input: Union[np.ndarray, str], normalize_by: int)-> np.ndarray:
        """
        Takes input image data (either as a numpy array or a file path), normalizes it, 
        converts it to the Lab color space using the "color science"(validation library),
        and then returns the resulting Lab validation data.

        :param input: Image data or path to the image file.
        :type input: numpy.ndarray or str
        :param normalize_by: Value to normalize the input array by.
        :type normalize_by: float
        :return: Lab validation data converted from the input.
        :rtype: numpy.ndarray
        """
        
        if not isinstance(input, np.ndarray):
                arr = cv2.imread(input, cv2.IMREAD_UNCHANGED)[:,:,::-1]
        else:
                arr = input
                
        arr = arr / normalize_by
        lab_validation = conv_sRGB_to_lab_externallib(arr)
        return lab_validation

        
def extract_lab(input: Union[np.ndarray, str], convert=True, todtype=np.uint16) -> np.ndarray:
        """
        takes input image data (either as a numpy array or a file path), converts it to the Lab color space, 
        using the functions from ImageAnalysis (internal) library,and returns the resulting Lab internal data

        :param input: Image data as a numpy array or path to the image file.
        :type input: Union[np.ndarray, str]
        :return: Lab internal data converted from the input.
        :rtype: numpy.ndarray
        """           
        if convert:
                if not isinstance(input, np.ndarray):
                        arr = readImage(input)
                else:
                        arr = input.astype(todtype)
        else:
                arr = input
        lab_internal = conv_sRGB_to_Lab_internallib(arr)
        return lab_internal


def conv_sRGB_to_Lab_internallib(im: np.ndarray) -> np.ndarray:
        """
        Convert image from sRGB color space to Lab color space using the function from internal ImageAnalysis library.

        :param im: Image data in the sRGB color space.
        :type im: numpy.ndarray
        :return: Image data converted to the Lab color space.
        :rtype: numpy.ndarray
        """
        return sRGB_to_lab(im)


def conv_sRGB_to_lab_externallib(im: np.ndarray) -> np.ndarray:
        """
        Convert image from sRGB color space to Lab color space using functions from external "color science" library.

        :param im: Image data in the sRGB color space.
        :type im: numpy.ndarray
        :return: Image data converted to the Lab color space.
        :rtype: numpy.ndarray
        """
        return colour.XYZ_to_Lab(colour.sRGB_to_XYZ(im)) 


def get_all_color_combinations(bit_list: List[List[Any]]) -> List[List[Any]]:
        """
        Generate an array with (almost, becasue step size is set to 255 for memory efficiency) all possible combinations of items (8-bit or 16 bit color channels) from the 
        provided list.

        :param bit_list: List of lists representing ranges to generate combinations. For example: for 16 bit --> [range(0,65536,256),range(0,65536,256),range(0,65536,256)]
        :type bit_list: List[List[Any]]
        :return: List of all possible combinations of colors.
        :rtype: List[List[Any]]
        """
        output_list = list(itertools.product(*bit_list))
        return output_list


def reshape_arr_dims(combination_arr: np.ndarray) -> np.ndarray:
        """
        Reshape the array dimensions based on factors of the total number of elements.
        Basically this function tries to create the best possible square or rectangular matrix (2D array)  given a 1D array

        :param combination_arr: Array representing combinations of colors.
        :type combination_arr: numpy.ndarray
        :return: Reshaped array with dimensions determined by factors of the total number of elements.
        :rtype: numpy.ndarray
        """   
        # Find factors of the total number of elements
        num_elements = combination_arr.shape[0]
        factor1 = int(np.sqrt(num_elements))
        
        while num_elements % factor1 != 0:
                factor1 -= 1
                
        factor2 = num_elements // factor1
        # Reshape using factors as x and y dims and 3 channels
        x = factor1
        y = factor2
        color_matrix = combination_arr.reshape(x, y, 3)
        return color_matrix


def get_dummy_color_matrix(bit_list: List[List[Any]]) -> np.ndarray:
        """
        Get the color matrix composed of almost all combinations of color bit lists.
        This will be used as the dummy validation array for testing the color conversion function.

        :param bit_list: List of lists representing different color bit combinations.
        :type bit_list: List[List[Any]]
        :return: Color matrix representing all possible combinations of colors.
        :rtype: numpy.ndarray
        """   
        combination_arr = np.array(get_all_color_combinations(bit_list))
        dummy_color_matrix = reshape_arr_dims(combination_arr)
        print("Color matrix shape:", dummy_color_matrix.shape)
        return dummy_color_matrix


def save_interim_results(lab_array: np.ndarray, outpath: str) -> None:
        """
        Save validation results to TSV files.

        :param lab_array: Lab array to be saved.
        :type lab_array: numpy.ndarray
        :param outpath: Path to save the TSV files.
        :type outpath: str
        :return: None
        """
        for n in range(0, 3):
                l = ["validation", "internal", "delta"]
                np.savetxt(os.path.join(outpath, f"{l[n]}_{n}.tsv"), lab_array[:, :, n], fmt='%.3f')

def main():
        """
        Run this script to validate the Lab converter functions
        """
        
        OUTPATH = r"D:\STUDIES\23.0264-99_Perrigo_Klifo_studie\data_validation\exported_data_validation_results"
        
        if not os.path.exists(OUTPATH):
                os.mkdir(OUTPATH)
        ### Constants for normalizing input before conversion - converter functions need values between 0-1
        # For 16 bit images
        list_16bit = [range(0,65536,256),range(0,65536,256),range(0,65536,256)]
        NORMALIZE_16bit = 65535
        
        # # Use for 8 bit images
        # list_8bit = [range(0, 256),range(0, 256),range(0, 256)]
        # NORMALIZE_8bit = 255

        ## Validation is performed on: 
        # - sRGB 16 bit randomly selected image
        SAMPLE_IMG_PATH = r"D:\Code\Software_test_sample_data\230264_Klifo_algos\LAB_extractor\sample.tif"
        
        # - a dummy matrix that approximately consists of all the shades in 16 bit color space
        dummy_color_matrix = get_dummy_color_matrix(list_16bit)
        subfolder_paths = [os.path.join(OUTPATH, name) for name in ["dummy_matrix", "sample_image"]]
        
        for nr, input in enumerate([dummy_color_matrix, SAMPLE_IMG_PATH]):
                lab_validation = extract_lab_validation(input, normalize_by=NORMALIZE_16bit)
                lab_internal = extract_lab(input)
                delta = np.abs(lab_validation - lab_internal)
                
                # print(delta.max())
                # print(delta.mean())
                
                print(f"{["dummy_matrix", "sample_image"][nr]} Mean: {delta.mean()}")
                
                # if not os.path.exists(subfolder_paths[nr]):
                #         os.mkdir(subfolder_paths[nr])
                # for lab_array in [lab_validation, lab_internal, delta]:
                #         save_interim_results(lab_array, subfolder_paths[nr]) # just for testing purposes


if __name__ == "__main__":
        main()
