import json
from random import randint
import os
from ImageAnalysis import ColorConversion as cc
from typing import Optional, Tuple

class InternalImport:
    """
    A class that manages the configuration, paths, color profiles, and test-specific details for image analysis.
    """
    
    def __init__(self) -> None:
        """
        Initializes the InternalImport class by reading configuration data and setting up relevant paths and test details.
        """
        data = self.__read_config_data()
        self.mypath: str = data['path']
        self.studynumber: str = data['stdyno']
        self.filename_mask: str = data['MASK']
        self.draft_flag: str = data['FAST_DRAFT']
        self.isVisia: str = data['Is_Visia']
        self.path_for_validation: str = self.mypath
        self.validated_path: str = "" 
        self.No_marketing: str = data['No_marketing']
        self.colorfile, self.colorname, self.file_extension = self.__get_colorprofile_specs(self.path_for_validation)
        self.Test_type, self.randomfilepath = self.__get_testinfo_for_output_folder_naming(data)
        self.header: str = self.__get_header(self.draft_flag)
        self.pagestyle: str = self.__get_pagestyle(self.No_marketing, self.studynumber)
        
        # Hyper setup for PDF export
        self.hypersetup: str = r"""\hypersetup{pdftitle={Image Export},
                                pdfauthor={User},
                                pdfauthortitle={CIO},
                                pdfcopyright={Copyright (C) abc company},
                                pdfsubject={Image Overview},
                                pdfkeywords={image, overview},
                                pdflicenseurl={none},
                                pdfcaptionwriter={owner name,
                                pdfcontactaddress={address},
                                pdfcontactcity={city name},
                                pdfcontactpostcode={pcode},
                                pdfcontactcountry={County},
                                pdfcontactemail={emailid},
                                pdfcontacturl={url of company website},
                                pdflang={en},
                                bookmarksopen=true,
                                bookmarksopenlevel=3,
                                hypertexnames=false,
                                linktocpage=true,
                                plainpages=false,
                                breaklinks}
                            """
        self.B_randomfilepath: Optional[str] = self.__check_for_b_randomfilepath(data)
            
        # Excel file and dummy log file setup
        self.excelfile: str = f'Layout_{self.studynumber}{self.Test_type}.xlsx'
        self.dummy_log_file: str = f'{self.Test_type}_missing.txt'

    def __read_config_data(self) -> dict:
        """
        Reads the configuration data from a JSON file.
        
        Returns:
            dict: A dictionary containing the configuration values.
        """
        input_json_path = input("Please provide the path of the Json configuration file for the study: ")
        try:
            with open(input_json_path, "r") as config_file:
                data = json.load(config_file)
            return data
        except FileNotFoundError:
            print(f"Error: The file at {input_json_path} was not found.")
            raise
        except json.JSONDecodeError:
            print(f"Error: The file at {input_json_path} is not a valid JSON file.")
            raise

    def __check_for_b_randomfilepath(self, data: dict) -> Optional[str]:
        """
        Checks for the existence of the 'B' key in the configuration data and returns its value if present.
        
        Args:
            data (dict): The configuration data.
        
        Returns:
            Optional[str]: The random file path for B or None if not found.
        """
        if "B" in data.keys():
            return data["B"]
        else:
            print("The 'B' key does not exist in the config file. Assigning None.")
            return None

    def __get_header(self, draft_flag: str) -> str:
        """
        Generates the LaTeX header based on the draft flag.
        
        Args:
            draft_flag (str): The draft flag to determine the document class and settings.
        
        Returns:
            str: The LaTeX header as a string.
        """
        if draft_flag == "False":
            return r"""\RequirePackage{pdf14}
            \documentclass[a4paper]{scrartcl}
            \usepackage{helvet}
            \renewcommand{\familydefault}{\sfdefault}
            \usepackage[utf8]{inputenc}
            \usepackage[export]{adjustbox}
            \usepackage{fancyhdr}
            \usepackage[left=1.00cm,right=1.00cm,top=0.50cm,bottom=1.50cm,headheight=1.50cm,headsep=0.5cm,footskip=0.5cm,includeheadfoot]{geometry}
            \setlength{\parindent}{0cm}
            \usepackage[pdfa]{hyperref}
            \usepackage{hyperxmp}
            \def\arraystretch{0.9}
            \usepackage{grffile}
            \usepackage{pdf14}
            \usepackage{silence}
            \WarningsOff*
            \ErrorsOff*

            \immediate\pdfobj stream attr{/N 3}  file{%s}
            \pdfcatalog{/OutputIntents [ <<
            /Type /OutputIntent
            /S/GTS_PDFA1
            /DestOutputProfile \the\pdflastobj\space 0 R
            /OutputConditionIdentifier (%s)
            /Info(%s)
            >> ]
            }
            """ % (self.colorfile, self.colorname, self.colorname)
        elif draft_flag == "True":
            return r"""\RequirePackage{pdf14}
                            \documentclass[a4paper, draft]{scrartcl}
                            \usepackage{helvet}
                            \renewcommand{\familydefault}{\sfdefault}
                            \usepackage[utf8]{inputenc}
                            \usepackage[export]{adjustbox}
                            \usepackage{fancyhdr}
                            \usepackage[left=1.00cm,right=1.00cm,top=0.50cm,bottom=1.50cm,headheight=1.50cm,headsep=0.5cm,footskip=0.5cm,includeheadfoot]{geometry}
                            \setlength{\parindent}{0cm}
                            \usepackage[pdfa]{hyperref}
                            \usepackage{hyperxmp}
                            \def\arraystretch{0.9}
                            \usepackage{grffile}
                            \usepackage{silence}
                            \WarningsOff*
                            \ErrorsOff*

                            \immediate\pdfobj stream attr{/N 3}  file{%s}
                            \pdfcatalog{/OutputIntents [ <<
                            /Type /OutputIntent
                            /S/GTS_PDFA1
                            /DestOutputProfile \the\pdflastobj\space 0 R
                            /OutputConditionIdentifier (%s)
                            /Info(%s)
                            >> ]
                            }
                            """ % (self.colorfile, self.colorname, self.colorname)
        
    def __get_pagestyle(self, marketing_flag: str, studynumber: str) -> str:
        """
        Returns the LaTeX page style based on the marketing flag and study number.
        
        Args:
            marketing_flag (str): The flag indicating if marketing is allowed.
            studynumber (str): The study number to include in the footer.
        
        Returns:
            str: The LaTeX page style configuration.
        """
        if marketing_flag == "True":
            return r"""\pagestyle{fancy}
            \rhead{\includegraphics[scale=0.5]{path to logo.png}}
            \lfoot{footer text 3 \\ footer text 2 \\ footer text 3}
            \cfoot{%s\\ Image Overview}
            \rfoot{Page \thepage}
            """ % (studynumber.replace('_', '\\_') )
        else:
            return r"""\pagestyle{fancy}
                \rhead{\includegraphics[scale=0.5]{path_to_logo/logo.jpg}}
                \lfoot{footer text 3 \\ footer text 2 }
                \cfoot{%s\\ Image Overview}
                \rfoot{Page \thepage}
                """ % (studynumber.replace('_', '\\_') )
        
    def __get_testinfo_for_output_folder_naming(self, data: dict) -> Tuple[str, Optional[str]]:
        """
        Prompts for test information and generates test output folder names based on user input and configuration data.
        
        Args:
            data (dict): The configuration data.
        
        Returns:
            Tuple[str, Optional[str]]: The test type and the random file path (if applicable).
        """
        user_input = input("What kind of test is this (S/T/SR/TR/C): ")
        counter = input("Iteration number: ")
        
        if counter == "":
            counter = str(randint(0, 100))
        
        if user_input.lower() == "s":
            return f"S_{counter}", None
        elif user_input.lower() == "t":
            return f"T_{counter}", None
        elif user_input.lower() == "sr":
            return f"SR_{counter}", data.get("RANDOM", None)
        elif user_input.lower() == "tr":
            return f"TR_{counter}", data.get("RANDOM", None)
        elif user_input.lower() == "c":
            return f"C_{counter}", data.get("RANDOM", None)

    def __get_colorprofile_specs(self, path_to_images: str) -> Tuple[str, str, str]:
        """
        Scans the directory for image files and retrieves the color profile of the first image found.
        
        Args:
            path_to_images (str): The path to the folder containing image files.
        
        Returns:
            Tuple[str, str, str]: The color profile file, the color profile name, and the image file type.
        """
        files_list = os.listdir(path_to_images)
        for f in files_list:
            if f.endswith(("jpg", "JPG")):
                return self.__process_image(path_to_images, f, "jpg")
            elif f.endswith("png"):
                return self.__process_image(path_to_images, f, "png")
            elif f.endswith(("tiff", "tif", "TIF")):
                return self.__process_image(path_to_images, f, "tif")
        raise FileNotFoundError("No supported image files found in the specified directory.")

    def __process_image(self, path_to_images: str, filename: str, file_type: str) -> Tuple[str, str, str]:
        """
        Processes the given image to extract its color profile.
        
        Args:
            path_to_images (str): The directory containing the image.
            filename (str): The image file name.
            file_type (str): The file type (jpg, png, or tif).
        
        Returns:
            Tuple[str, str, str]: The color profile file, color profile name, and image file type.
        """
        filepath = os.path.join(path_to_images, filename)
        colorspace_tuple = cc.get_colorprofile(filepath)
        return self.__color_profile_elements(colorspace_tuple), file_type

    def __color_profile_elements(self, colorspace_tuple: Tuple[str, str]) -> Tuple[str, str]:
        """
        Extracts the color profile elements based on the colorspace tuple.
        
        Args:
            colorspace_tuple (Tuple[str, str]): The colorspace information extracted from the image.
        
        Returns:
            Tuple[str, str]: The color profile file and name.
        """
        try:
            if colorspace_tuple[0] == 'srgb':
                colorfile = 'path_to_sRGB_profile'
                colorname = "sRGB Color Space Profile"
                return colorfile, colorname
            elif colorspace_tuple[0] == 'adobe':
                colorfile = 'path_to_AdobeRGB_profile'
                colorname = "adobeRGB Color Space Profile"
                return colorfile, colorname
        except IndexError:
            print("No color profile found, applying default sRGB.")
            return 'path_to_sRGB_profile', "sRGB Color Space Profile"
