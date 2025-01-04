# run auto-py-to-exe to generate executable


import os

import win32file
import win32event
import win32con
import PySimpleGUI as psg
from matplotlib import pyplot as plt
# path_to_watch = r"D:\Code\Software_test_sample_data\Dev_Projejct13_OutOfFocus_imageclssifier\test_watchdir"
# import the necessary packages
import cv2
import os
import numpy as np
import regex as re
import numpy as np
from typing import Dict, Tuple
# THRESH = 2.1

import logging

# Create a custom logger
logger = logging.getLogger(__name__)
log_file_name = "Blur_detect_GUI.log"
# Configure the logger
logging.basicConfig(filename=log_file_name, \
level=logging.DEBUG, \
format='%(asctime)s :: %(levelname)s :: Module %(module)s :: Line No %(lineno)s :: %(message)s')

# Create handlers
c_handler = logging.StreamHandler()

c_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
# Add handlers to the logger
logger.addHandler(c_handler)

# logger.warning('This is a warning')
# logger.error('This is an error')

def variance_of_laplacian(gray_img: np.ndarray) -> float:
    """
    Computes the Laplacian of the image and returns the focus measure, which is simply the variance of the Laplacian.

    :param gray_img: Grayscale input image
    :return: Variance of the Laplacian (focus measure)
    """
    return cv2.Laplacian(gray_img, cv2.CV_64F).var()


def calculate_average_grayscale(roi: np.ndarray) -> np.ndarray:
    """
    Calculates the average grayscale value of the given region of interest.

    :param roi: Region of interest (color image)
    :return: Grayscale image
    """
    gray = np.dot(roi, [0.2989, 0.5870, 0.1140]).astype(np.uint8)
    return gray


def check_image_for_blurryness(img_path: str, thresh: float, white_thresh: float, 
                               img_slice: tuple, white_card_dict: dict, white_found_flag: int, Testing: bool) -> tuple:
  """
  Checks if an image is blurry and detects white card presence.

  :param img_path: Path to the image file
  :param thresh: Blur threshold
  :param white_thresh: White card detection threshold
  :param img_slice: Tuple defining the region of interest
  :param white_card_dict: Dictionary to track white card status
  :param white_found_flag: Flag indicating if white card was found
  :param Testing: Boolean to enable/disable testing mode
  :return: Tuple containing overall status, white found flag, updated white card dictionary, and mean intensity
  """
  image = cv2.imread(img_path) 
  #image[start_row, end_row, start_column, end_column].
  
  # Extract the region of interest
  roi = image[img_slice[0]:img_slice[1], img_slice[2]:img_slice[3]]
  
  # Convert to grayscale using the new method
  gray = calculate_average_grayscale(roi)


  # OLD method
  # gray = cv2.cvtColor(image[img_slice[0]:img_slice[1],img_slice[2]:img_slice[3]], cv2.COLOR_BGR2GRAY)

  if Testing==True:
    plt.imshow(image)
    plt.imshow(gray)
    plt.show()

  white_found_flag, white_card_dict, white_found_status, mean_intensity = check_white(img_path, white_thresh, 
                                                                                      white_card_dict, white_found_flag, gray)
  
  blur_factor = variance_of_laplacian(gray)
  
  if blur_factor > thresh:
      overall_status = f"\t In Focus" + f"\t{blur_factor}" + f"\t{img_path}" + f"\t{white_found_status}" + f"\t{white_found_flag}"
  elif blur_factor < thresh: # if the focus measure is less than the supplied threshold, then the image should be considered "blurry"
      overall_status = f"\t Out of Focus" + f"\t{blur_factor}" + f"\t{img_path}" + f"\t{white_found_status}" + f"\t{white_found_flag}"
  return overall_status, white_found_flag, white_card_dict, mean_intensity	



def check_white(img_path: str, white_thresh: float, white_card_dict: Dict[str, int], 
                white_found_flag: int, gray: np.ndarray) -> Tuple[int, Dict[str, int], str, float]:
  """
  Check if a white calibration card is present in the image and update the white card status.

  This function analyzes the grayscale image to determine if a white calibration card is present
  based on the mean intensity and a given threshold. It updates the white card dictionary and
  status flags accordingly.

  :param img_path: Path to the image file
  :param white_thresh: Threshold for white card detection
  :param white_card_dict: Dictionary tracking white card status for each image
  :param white_found_flag: Flag indicating if a white card was previously found
  :param gray: Grayscale image array
  :return: Tuple containing updated white_found_flag, white_card_dict, white_found_status, and mean_intensity
  """
 
  mean_intensity = np.mean(gray)
  # white_threshold = 190 # Adjust this threshold as per your requirement
  img_name = img_path.split("\\")[-1]
  if "S" not in img_name and "F" not in img_name and "T" not in img_name:
    logger.debug("Not Standard barcode during image blurry white check")
  else:
    img_name = re.search(r"S[0-9]{3}F[0-9]{2}T[0-9]{2}", img_name).group(0)
    # img_name = img_path.split("\\")[-1].split("_")[0]
    
  if img_name not in  white_card_dict.keys():
    white_found_flag = 0
    white_card_dict[img_name] = white_found_flag
    logger.debug("Adding filename to dict first time")
    logger.debug(white_card_dict)
    # input("Press Enter to continue")
  if white_found_flag == 1:
    logger.debug("White OK - Bild fuer Barcode schon aufgennomen")
    logger.debug(f"white flag : {white_found_flag}")
    white_found_status = "White Image - OK"
    logger.debug("White card for barcode already present")
    logger.debug(white_card_dict)
    # input("Press Enter to continue")
    return white_found_flag, white_card_dict, white_found_status, mean_intensity
  
  elif mean_intensity > white_thresh:
    white_found_flag = 1
    white_card_dict[img_name] = white_found_flag
    logger.debug("White OK")
    logger.debug(f"white flag : {white_found_flag}")
    logger.debug("white card finally found, barcode dict changed from 0 to 1")
    logger.debug(white_card_dict)
    # input("Press Enter to continue")
    white_found_status = "White Image - Found"

  else:
    logger.debug("White Image Missing")
    logger.debug(f"white flag : {white_found_flag}")
    logger.debug("white card still missing")
    logger.debug(white_card_dict)
    # input("Press Enter to continue")
    white_found_status = "White Image - Missing"

  return white_found_flag, white_card_dict, white_found_status, mean_intensity

def watch_dir(pathtowatch: str, Threshold: float, WhiteCard_thresh: float, freeze_count: int, img_slice: tuple, testing: bool) -> None:
  """
  Watches a directory for file changes and processes new images.

  :param pathtowatch: Directory path to watch
  :param Threshold: Blur detection threshold
  :param WhiteCard_thresh: White card detection threshold
  :param freeze_count: Maximum wait count before timeout
  :param img_slice: Tuple defining the region of interest
  :param testing: Boolean to enable/disable testing mode
  """
  change_handle = win32file.FindFirstChangeNotification (pathtowatch, 0, win32con.FILE_NOTIFY_CHANGE_FILE_NAME)

  timeout_count = 0
  try:
    old_path_contents = dict([(f, None) for f in os.listdir (pathtowatch) if not (f.endswith(".ini") or f.endswith(".cr2"))])

    # Loop forever, listing any file changes. The WaitFor... will time out every half a second allowing for keyboard interrupts to terminate the loop.
    white_card_state_dict = {}
    white_found_flag = 0
    while True:
      result = win32event.WaitForSingleObject(change_handle, 500)
      if result == 258: # waitkey code from windows api
        timeout_count += 1
        if timeout_count == freeze_count:
          print("waited too long....leaving custum loop")
          print(f"{timeout_count} reached, sleeping")
          psg.popup('Waited too long...sleeping. Press Enter to continue', button_color="red", keep_on_top=True, any_key_closes=True)
          timeout_count = 0
      # If the WaitFor... returned because of a notification (as opposed to timing out or some error) then look for the changes in the directory contents.
      print(result)
      if result == win32con.WAIT_OBJECT_0:
        new_path_contents = dict([(f, None) for f in os.listdir (pathtowatch) if not (f.endswith(".ini") or f.endswith(".cr2"))])
        added = [f for f in new_path_contents if not f in old_path_contents]
        deleted = [f for f in old_path_contents if not f in new_path_contents]

        val = None

        if added: 
          logger.info("Added: " + ", ".join (added))
          logger.debug(f"added list lenght : {len(added)}")
          if len(added) == 1 and (added[0].endswith("JPG") or added[0].endswith("jpg")):
            filename = added[0]
            logger.debug(filename)
            
            val, white_found_flag, white_card_state_dict, mean_intensity = check_image_for_blurryness(os.path.join(pathtowatch, filename),
                                                                                                      Threshold, 
                                                                                                      WhiteCard_thresh, img_slice, 
                                                                                                      white_card_state_dict, white_found_flag, 
                                                                                                      testing)
            logger.debug(val)
            val = val.split("\t")
            logger.debug(val)

          elif len(added) == 2 and (added[1].endswith("JPG") or added[1].endswith("jpg")):
            filename = added[1]
            logger.debug(filename)

            val, white_found_flag, white_card_state_dict,mean_intensity= check_image_for_blurryness(os.path.join(pathtowatch, filename), 
                                                                                Threshold, WhiteCard_thresh, img_slice,  
                                                                                white_card_state_dict, white_found_flag, testing)
            logger.debug(val)
            val = val.split("\t")
            logger.debug(val)

          logger.info("Output generated...")
          
          if val != None:
            # out_signal = psg.PopupYesNo((val[1], val[2], val[-1].split("\\")[-1]), title="Is the filename correct?", text_color='Black', font=("Arial",30,"bold"))
            
            out_signal = custom_popup(val, Threshold, pathtowatch, old_path_contents, mean_intensity, WhiteCard_thresh, freeze_count)
            print(out_signal)

            if out_signal == "No":
              while True:

                corrected_barcode = psg.popup_get_text(message="Enter correct name or scan correct barcode")
                logger.debug(corrected_barcode)
                if corrected_barcode != None and isinstance(corrected_barcode, str):
                  if corrected_barcode == "":
                    logger.error(f"Empty string error, prompting again")
                    continue

                  image_path_wrg_barcode = val[3]
                  wrg_barcode = image_path_wrg_barcode.split("\\")[-1]
                  extn = "." + image_path_wrg_barcode.split("_")[-1].split(".")[-1]
                  # handles filename other than standard barcode formats
                  if "S" not in wrg_barcode and "F" not in wrg_barcode and "T" not in wrg_barcode:
                    logger.warning("Not Standard barcode")
                    logger.warning("replacement details:")
                    logger.warning(corrected_barcode, wrg_barcode.replace(extn, ""))
                  else:
                    wrg_barcode_without_imgcounter = wrg_barcode.split("_")[0]
                    wrg_imgcounter = wrg_barcode.split("_")[-1].replace(extn, "")

                    logger.debug("Old image split to:")
                    logger.debug(wrg_barcode_without_imgcounter, wrg_imgcounter)
                  
                  imgpath_correct_barcode = os.path.join("\\".join(image_path_wrg_barcode.split("\\")[:-1]), corrected_barcode+ ".." +extn)
                  try:
                    # Rename JPGs
                    os.rename(image_path_wrg_barcode, imgpath_correct_barcode)
                    logger.info("Jpgs renamed")
                    logger.info(image_path_wrg_barcode, imgpath_correct_barcode)
                    
                    # Rename Raw 
                    os.rename(image_path_wrg_barcode.replace(".jpg", ".cr2").replace(".JPG", ".CR2"), imgpath_correct_barcode.replace(".jpg", ".cr2").replace(".JPG", ".CR2"))
                    logger.info("Cr2 renamed")
                    logger.info(image_path_wrg_barcode.replace(".jpg", ".cr2").replace(".JPG", ".CR2"), imgpath_correct_barcode.replace(".jpg", ".cr2").replace(".JPG", ".CR2"))
                    
                    os.rename(image_path_wrg_barcode.replace(".jpg", ".ini").replace(".JPG", ".ini"), imgpath_correct_barcode.replace(".jpg", ".ini").replace(".JPG", ".ini"))
                    logger.info("ini renamed")
                    logger.info(image_path_wrg_barcode.replace(".jpg", ".ini").replace(".JPG", ".ini"), imgpath_correct_barcode.replace(".jpg", ".ini").replace(".JPG", ".ini"))
                  except FileNotFoundError:
                    logger.error(FileNotFoundError)
                    logger.error(image_path_wrg_barcode, imgpath_correct_barcode)
                  break

                elif corrected_barcode == None:
                  logger.warning("User canceled renaming msg box...returning to main event loop")
                  break

            if out_signal == 2:
              continue

            elif out_signal != ("No" or "Yes" or None):
              old_path_contents = new_path_contents
              continue

        if deleted: 
          logger.info("Deleted: ", ", ".join (deleted))

        old_path_contents = new_path_contents
        win32file.FindNextChangeNotification(change_handle)
        
  finally:
    win32file.FindCloseChangeNotification(change_handle)

def custom_popup(list_of_texts: list, thresh_val: float, path_watched: str, 
                 OldPathContents: dict, mean_intensity: float, white_thresh: float, freeze_count: int) -> str:
  """
  Creates a custom popup window for user interaction.

  :param list_of_texts: List of text elements to display
  :param thresh_val: Blur threshold value
  :param path_watched: Directory being watched
  :param OldPathContents: Dictionary of old path contents
  :param mean_intensity: Mean intensity of the image
  :param white_thresh: White card detection threshold
  :param freeze_count: Maximum wait count before timeout
  :return: User's response as a string
  """

  try:
    barcode = list_of_texts[3].split("\\")[-1]

    subj = re.search(r"S[0-9]{3}", barcode).group(0)
    side = re.search(r"F[0-9]{2}", barcode).group(0)
    timepoint = re.search(r"T[0-9]{2}", barcode).group(0)
    barcode_with_spacing = subj + "  " + side + "  "+ timepoint

  except AttributeError:
    print("Barcode not found...returning original name")
    barcode_with_spacing = barcode

  focus_status = list_of_texts[1]
  blur_factor = list_of_texts[2]
  white_card_status = list_of_texts[4]

  # for every white card
  layout_OutOfFocusGrey_WhiteFound = [
    [psg.Text(focus_status, size=(20, 1), text_color="DimGrey", font=("Arial",10))],
    [psg.Text(blur_factor, size=(20, 1), text_color="DimGrey", font=("Arial", 10))],
    [psg.Text(white_card_status, size=(40, 1), text_color="OliveDrab1", font=("Arial", 40, "bold"))],
    [psg.Text(str(mean_intensity), size=(10, 1), text_color="OliveDrab1", font=("Arial", 10, "bold"))],
    [psg.Text(barcode_with_spacing, size=(40, 1), text_color="Black", font=("Arial", 80, "bold"))],
    [psg.Text("Is the barcode correct?", size=(20, 1), text_color="Black", font=("Arial",10))],
    [psg.Button('Yes', key = '-YES-'), psg.Button('No', key='-NO-')],
    [psg.Text("Take an image to continue without changes", text_color="FloralWhite", font=("Arial",10, "italic"))]]
  
  layout_OutOfFocusRed_WhiteFound = [
    [psg.Text(focus_status, size=(20, 1), text_color="OrangeRed2", font=("Arial",40, "bold"))],
    [psg.Text(blur_factor, size=(20, 1), text_color="OrangeRed2", font=("Arial", 10))],
    [psg.Text(white_card_status, size=(40, 1), text_color="OliveDrab1", font=("Arial", 40, "bold"))],
    [psg.Text(str(mean_intensity), size=(10, 1), text_color="OliveDrab1", font=("Arial", 10, "bold"))],
    [psg.Text(barcode_with_spacing, size=(40, 1), text_color="Black", font=("Arial", 80, "bold"))],
    [psg.Text("Is the barcode correct?", size=(20, 1), text_color="Black", font=("Arial",10))],
    [psg.Button('Yes', key = '-YES-'), psg.Button('No', key='-NO-')],
    [psg.Text("Take an image to continue without changes", text_color="FloralWhite", font=("Arial",10, "italic"))]]

  # worst case no white card, no focused pic
  layout_OutOfFocus_WhiteNotFound = [
    [psg.Text(focus_status, size=(40, 1), text_color="OrangeRed2", font=("Arial",40, "bold"))],
    [psg.Text(blur_factor, size=(20, 1), text_color="OrangeRed2", font=("Arial",10))],
    [psg.Text(white_card_status, size=(40, 1), text_color="IndianRed3", font=("Arial",40, "bold"))],
    [psg.Text(str(mean_intensity), size=(10, 1), text_color="IndianRed3", font=("Arial",10, "bold"))],
    [psg.Text(barcode_with_spacing, size=(20, 1), text_color="Black", font=("Arial",80, "bold"))],
    [psg.Text("Is the barcode correct?", size=(20, 1), text_color="Black", font=("Arial",10))],
    [psg.Button('Yes', key = '-YES-'), psg.Button('No', key='-NO-')],
    [psg.Text("Take an image to continue without changes", text_color="FloralWhite", font=("Arial",10, "italic"))]]
  
  # best case both images taken
  layout_InFocus_WhiteFound = [ 
    [psg.Text(focus_status, size=(40, 1), text_color="green1", font=("Arial",40))],
    [psg.Text(blur_factor, size=(20, 1), text_color="green2", font=("Arial",10))],
    [psg.Text(white_card_status, size=(40, 1), text_color="OliveDrab1", font=("Arial",10, "bold"))],
    [psg.Text(str(mean_intensity), size=(40, 1), text_color="OliveDrab1", font=("Arial",10, "bold"))],
    [psg.Text(barcode_with_spacing, size=(40, 1), text_color="Black", font=("Arial",80,"bold"))],
    [psg.Text("Is the barcode correct?", size=(20, 1), text_color="Black", font=("Arial",10))],
    [psg.Button('Yes', key = '-YES-'), psg.Button('No', key='-NO-')],
    [psg.Text("Take an image to continue without changes", text_color="FloralWhite", font=("Arial",10, "italic"))]]

  # reminder to take white pic, good color image focus
  layout_InFocus_WhiteNotFound = [ 
    [psg.Text(focus_status, size=(40, 1), text_color="green1", font=("Arial",40))],
    [psg.Text(blur_factor, size=(20, 1), text_color="green2", font=("Arial",10,))],
    [psg.Text(white_card_status, size=(40, 1), text_color="IndianRed3", font=("Arial",40, "bold"))],
    [psg.Text(str(mean_intensity), size=(40, 1), text_color="IndianRed3", font=("Arial",10, "bold"))],
    [psg.Text(barcode_with_spacing, size=(40, 1), text_color="Black", font=("Arial",80,"bold"))],
    [psg.Text("Is the barcode correct?", size=(20, 1), text_color="Black", font=("Arial",10))],
    [psg.Button('Yes', key = '-YES-'), psg.Button('No', key='-NO-')],
    [psg.Text("Take an image to continue without changes", text_color="FloralWhite", font=("Arial",10, "italic"))]]
  
  if int(list_of_texts[5]) == 1 and float(list_of_texts[2]) >= thresh_val: # in focus and white found
    window = psg.Window('CustomPopup', layout_InFocus_WhiteFound, finalize=True, location= (0, 1000))
  elif int(list_of_texts[5]) == 0 and float(list_of_texts[2]) >= thresh_val: # in focus and white not found
    window = psg.Window('CustomPopup', layout_InFocus_WhiteNotFound, finalize=True, location= (0, 1000))
  elif int(list_of_texts[5]) == 1 and float(list_of_texts[2]) < thresh_val and mean_intensity > white_thresh: # out of  focus and white found
    window = psg.Window('CustomPopup', layout_OutOfFocusGrey_WhiteFound, finalize=True, location= (0, 1000))
  elif int(list_of_texts[5]) == 1 and float(list_of_texts[2]) < thresh_val and mean_intensity < white_thresh:
    window = psg.Window('CustomPopup', layout_OutOfFocusRed_WhiteFound, finalize=True, location= (0, 1000))
  else:# out of focus and white not found
    window = psg.Window('CustomPopup', layout_OutOfFocus_WhiteNotFound, finalize=True, location= (0, 1000))

  freeze_counter = 0
  while True:
    
    event, values = window.Read(timeout=0)
    logger.debug(event)
    logger.debug(values)
    if event == psg.WIN_CLOSED:
      logger.warning(f"Closing {event}")
      window.close()
      return "None"
    elif event == "-YES-":
      window.close()
      return "Yes"
    elif event == "-NO-":
      window.close()
      return "No"
    wait_key = watch_dir_simple(path_watched, OldPathContents)
    if wait_key == 0:
      window.close()
      logger.debug("waitkey 0 returned - new file detected in custom popup loop")
      return wait_key
    elif wait_key == 2:
      window.close()
      logger.debug("waitkey 2 returned in custom_popup loop")
      return wait_key
    if event == psg.TIMEOUT_EVENT:
      print("Time out event detected")
      freeze_counter += 1 
      print(freeze_counter)
      if freeze_counter == freeze_count:
        print("waited too long....leaving custum loop")
        print(f"{freeze_counter} reached, sleeping")
        psg.popup('Waited too long...sleeping. Press Enter to continue', button_color="red", keep_on_top=True, any_key_closes=True)
        window.close()
        break
    print("looping again")

def watch_dir_simple(pathtowatch: str, old_path_contents: Dict[str, None]) -> int:
  """
  Watch a directory for file changes and return the status of the changes.

  This function sets up a handle to watch for file changes in the specified directory.
  It waits for a short period and then checks for any added or deleted files.

  :param pathtowatch: The path to the directory to watch
  :param old_path_contents: A dictionary containing the previous contents of the directory
  :return: An integer representing the status of the changes:
            - 258: Timeout occurred (no changes detected)
            - 1: Changes detected, but no files added or deleted
            - 2: Files were deleted
            - 0: New files were added
  """ 
  change_handle = win32file.FindFirstChangeNotification (pathtowatch, 0, win32con.FILE_NOTIFY_CHANGE_FILE_NAME)

  # Loop forever, listing any file changes. The WaitFor... will time out every half a second allowing for keyboard interrupts to terminate the loop.

  result = win32event.WaitForSingleObject(change_handle, 500)
  # If the WaitFor... returned because of a notification (as opposed to timing out or some error) then look for the changes in the directory contents.

  new_path_contents = dict([(f, None) for f in os.listdir (pathtowatch) if not (f.endswith(".ini") or f.endswith(".cr2"))])
  added = [f for f in new_path_contents if not f in old_path_contents]
  deleted = [f for f in old_path_contents if not f in new_path_contents]

  if added: 
    logger.info("Added again: " + ", ".join (added))
    return result

  if deleted: 
    logger.info("Deleted: " + ", ".join (deleted))
    logger.info("Files removed - returning 2 in watchdir simple loop ")
    return 2

    # old_path_contents = new_path_contents
    # win32file.FindNextChangeNotification(change_handle)
  else:
    logger.info("All okay - returning 1 inside watchdir simple loop and exiting loop")
    return 1

  # finally:
  #   win32file.FindCloseChangeNotification(change_handle)

def main():
  """
  main _summary_
  """ 
  Row_Vert_Y1, Col_Horz_X1, Height_Vert_Y2, Width_Horz_X2 = 800, 1800, 2300, 2200
  STD_THRESH = 5
  STD_WHITE_THRESH = 190
  SLEEP_DUR = 2
  TESTING = False
  #Standard for Dermlite [800:800+2300,1800:1800+2200] ---> Open CV slicing [Row_Vert_Y1 : Row_Vert_Y1 + Height_Vert_Y2, Col_Horz_X1 : Col_Horz_X1 + Width_Horz_X2]
  img_slice = (Row_Vert_Y1, Row_Vert_Y1 + Height_Vert_Y2 , Col_Horz_X1 , Col_Horz_X1 + Width_Horz_X2)
  layout = [[psg.Text('Enter the folderpath to be tracked', key='-TEXT1-'), psg.Input(key='-FPATH-')],
  [psg.Text('Enter the focus threshold', key='-TEXT2-'), psg.Input(default_text="5", size=(5, 1), key='-THRESHF-')],
  [psg.Text('Enter the white card threshold',  key='-TEXT3-'), psg.Input(default_text="190", size=(5, 1), key='-THRESHW-')],
  [psg.Text('Sleeps after (X min)',  key='-TEXT4-'), psg.Input(default_text="2", size=(5, 1), key='-SLEEPAFTER-')],
  [psg.Button('Start', key = '-START-')]]

  window = psg.Window('convertor', layout)

  while True:
    event, values = window.read()
    print(event)
    print(values)
    if event ==psg.WIN_CLOSED:
        logger.info(f"Closing before starting  - main_loop")
        break
    try:
      out_val = watch_dir(values['-FPATH-'], float(values['-THRESHF-']), float(values['-THRESHW-']), int(values["-SLEEPAFTER-"])*60, img_slice, TESTING)

    except ValueError:
      std_dict = {'-FPATH-': None, '-THRESHF-': STD_THRESH, '-THRESHW-': STD_WHITE_THRESH, "-SLEEPAFTER-": SLEEP_DUR }
      values_default = {k:std_dict[k] for k, v in values if v == ""}
      print("Some values missing, defaults will be used")
      
      out_val = watch_dir(values_default['-FPATH-'], float(values_default['-THRESHF-']), float(values_default['-THRESHW-']), int(values_default["-SLEEPAFTER-"])*60, img_slice, TESTING)

    if out_val != None:
        window['-OUTPUT-'].update(str(out_val), visible=True)

  window.close()

if __name__ == "__main__":
  main()
  # Call the function to log messages
  # logger_example_function()

