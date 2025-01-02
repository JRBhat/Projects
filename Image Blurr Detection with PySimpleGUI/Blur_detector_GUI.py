import os
import win32file
import win32event
import win32con
import PySimpleGUI as psg
from matplotlib import pyplot as plt
import cv2
import numpy as np
import regex as re
import logging

# Create a custom logger
logger = logging.getLogger(__name__)
log_file_name = "Blur_detect_GUI.log"
logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format='%(asctime)s :: %(levelname)s :: Module %(module)s :: Line No %(lineno)s :: %(message)s')

# Create handlers
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
# Add handlers to the logger
logger.addHandler(c_handler)

def variance_of_laplacian(gray_img: np.ndarray) -> float:
    """
    Computes the Laplacian of the image and returns the focus measure, which is the variance of the Laplacian.

    :param gray_img: The grayscale image to evaluate
    :type gray_img: np.ndarray
    :return: The variance of the Laplacian, a measure of image focus
    :rtype: float
    """
    return cv2.Laplacian(gray_img, cv2.CV_64F).var()

def calculate_average_grayscale(roi: np.ndarray) -> np.ndarray:
    """
    Calculates the average grayscale value of a region of interest (ROI) by averaging the RGB values and converting them to grayscale.

    :param roi: The region of interest (ROI) in the image
    :type roi: np.ndarray
    :return: The grayscale version of the ROI
    :rtype: np.ndarray
    """
    average_rgb = np.mean(roi, axis=(0, 1))
    gray = np.dot(roi, [0.2989, 0.5870, 0.1140]).astype(np.uint8)
    return gray

def check_image_for_blurryness(img_path: str, thresh: float, white_thresh: int, img_slice: tuple, 
                               white_card_dict: dict, white_found_flag: int, Testing: bool) -> tuple:
    """
    Checks if the given image is blurry by calculating the variance of the Laplacian. Also checks for a white card based on intensity threshold.

    :param img_path: The path of the image to check
    :type img_path: str
    :param thresh: The blur threshold
    :type thresh: float
    :param white_thresh: The white intensity threshold
    :type white_thresh: int
    :param img_slice: The slice specifying the region of interest (ROI) in the image
    :type img_slice: tuple
    :param white_card_dict: A dictionary to track the white card status for each image
    :type white_card_dict: dict
    :param white_found_flag: The flag indicating whether the white card has been found (1 for found, 0 for not)
    :type white_found_flag: int
    :param Testing: A flag to indicate if the image is being tested for visualization
    :type Testing: bool
    :return: A tuple containing the overall status, white_found_flag, updated white_card_dict, and mean intensity
    :rtype: tuple
    """
    image = cv2.imread(img_path)
    roi = image[img_slice[0]:img_slice[1], img_slice[2]:img_slice[3]]
    gray = calculate_average_grayscale(roi)

    if Testing:
        plt.imshow(image)
        plt.imshow(gray)
        plt.show()

    white_found_flag, white_card_dict, white_found_status, mean_intensity = check_white(
        img_path, white_thresh, white_card_dict, white_found_flag, gray)
    
    blur_factor = variance_of_laplacian(gray)
    
    if blur_factor > thresh:
        overall_status = f"\t In Focus" + f"\t{blur_factor}" + f"\t{img_path}" + f"\t{white_found_status}" + f"\t{white_found_flag}"
    else:
        overall_status = f"\t Out of Focus" + f"\t{blur_factor}" + f"\t{img_path}" + f"\t{white_found_status}" + f"\t{white_found_flag}"
    
    return overall_status, white_found_flag, white_card_dict, mean_intensity

def check_white(img_path: str, white_thresh: int, white_card_dict: dict, white_found_flag: int, gray: np.ndarray) -> tuple:
    """
    Checks for the presence of a white card in the image by evaluating its mean intensity.

    :param img_path: The path of the image to check
    :type img_path: str
    :param white_thresh: The intensity threshold for detecting a white card
    :type white_thresh: int
    :param white_card_dict: A dictionary tracking the white card status for each image
    :type white_card_dict: dict
    :param white_found_flag: The flag indicating if the white card has been found
    :type white_found_flag: int
    :param gray: The grayscale image to analyze
    :type gray: np.ndarray
    :return: A tuple containing the updated white_found_flag, white_card_dict, white_found_status, and mean intensity
    :rtype: tuple
    """
    mean_intensity = np.mean(gray)
    img_name = img_path.split("\\")[-1]
    
    if "S" not in img_name and "F" not in img_name and "T" not in img_name:
        logger.debug("Not Standard barcode during image blurry white check")
    else:
        img_name = re.search(r"S[0-9]{3}F[0-9]{2}T[0-9]{2}", img_name).group(0)
    
    if img_name not in white_card_dict.keys():
        white_found_flag = 0
        white_card_dict[img_name] = white_found_flag
        logger.debug("Adding filename to dict first time")
    
    if white_found_flag == 1:
        logger.debug("White OK - Bild fuer Barcode schon aufgenommen")
        white_found_status = "White Image - OK"
        return white_found_flag, white_card_dict, white_found_status, mean_intensity
    
    if mean_intensity > white_thresh:
        white_found_flag = 1
        white_card_dict[img_name] = white_found_flag
        white_found_status = "White Image - Found"
    else:
        white_found_status = "White Image - Missing"

    return white_found_flag, white_card_dict, white_found_status, mean_intensity

def watch_dir(pathtowatch: str, Threshold: float, WhiteCard_thresh: int, freeze_count: int, 
              img_slice: tuple, testing: bool) -> None:
    """
    Watches a directory for added or deleted files. If a new image is added, checks its focus and white card status.

    :param pathtowatch: The path of the directory to watch
    :type pathtowatch: str
    :param Threshold: The threshold for detecting blurry images
    :type Threshold: float
    :param WhiteCard_thresh: The threshold for detecting a white card
    :type WhiteCard_thresh: int
    :param freeze_count: The number of timeouts before the function exits
    :type freeze_count: int
    :param img_slice: The region of interest (ROI) slice to analyze
    :type img_slice: tuple
    :param testing: Flag indicating if the function is in testing mode
    :type testing: bool
    """
    change_handle = win32file.FindFirstChangeNotification(pathtowatch, 0, win32con.FILE_NOTIFY_CHANGE_FILE_NAME)
    
    timeout_count = 0
    try:
        old_path_contents = dict([(f, None) for f in os.listdir(pathtowatch) if not (f.endswith(".ini") or f.endswith(".cr2"))])
        white_card_state_dict = {}
        white_found_flag = 0
        
        while True:
            result = win32event.WaitForSingleObject(change_handle, 500)
            if result == 258:
                timeout_count += 1
                if timeout_count == freeze_count:
                    print("Waited too long, exiting.")
                    psg.popup('Waited too long...sleeping. Press Enter to continue', button_color="red", keep_on_top=True, any_key_closes=True)
                    timeout_count = 0

            if result == win32con.WAIT_OBJECT_0:
                new_path_contents = dict([(f, None) for f in os.listdir(pathtowatch) if not (f.endswith(".ini") or f.endswith(".cr2"))])
                added = [f for f in new_path_contents if f not in old_path_contents]
                deleted = [f for f in old_path_contents if f not in new_path_contents]

                if added:
                    logger.info("Added: " + ", ".join(added))
                    if len(added) == 1 and (added[0].endswith("JPG") or added[0].endswith("jpg")):
                        filename = added[0]
                        val, white_found_flag, white_card_state_dict, mean_intensity = check_image_for_blurryness(
                            os.path.join(pathtowatch, filename), Threshold, WhiteCard_thresh, img_slice, 
                            white_card_state_dict, white_found_flag, testing)

                if deleted:
                    logger.info("Deleted: ", ", ".join(deleted))

                old_path_contents = new_path_contents
                win32file.FindNextChangeNotification(change_handle)
                
    finally:
        win32file.FindCloseChangeNotification(change_handle)

def custom_popup(list_of_texts: list[str], thresh_val: float, path_watched: str, 
                 OldPathContents: dict[str, None], mean_intensity: float, 
                 white_thresh: float, freeze_count: int) -> str:
  """
  Display a custom popup based on the status of a barcode image and the threshold values for focus and white card detection.
  
  :param list_of_texts: List containing status information (focus, blur factor, white card status, etc.)
  :type list_of_texts: list of str
  :param thresh_val: Threshold value to determine if the image is in focus.
  :type thresh_val: float
  :param path_watched: Path to the folder being monitored for changes.
  :type path_watched: str
  :param OldPathContents: Dictionary holding the current contents of the watched directory.
  :type OldPathContents: dict of str to None
  :param mean_intensity: Average intensity of the image for evaluating the white card presence.
  :type mean_intensity: float
  :param white_thresh: Threshold value for white card intensity.
  :type white_thresh: float
  :param freeze_count: Number of timeout events before the function exits.
  :type freeze_count: int
  :return: Result of the popup interaction or directory status.
  :rtype: str
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

def watch_dir_simple(pathtowatch: str, old_path_contents: dict[str, None]) -> int:
  """
  Monitors a directory for file changes and returns a status based on added or deleted files.
  
  :param pathtowatch: Path to the directory being monitored for changes.
  :type pathtowatch: str
  :param old_path_contents: Dictionary holding the current contents of the watched directory.
  :type old_path_contents: dict of str to None
  :return: Status code indicating file changes (0 = new file, 1 = no changes, 2 = file deleted).
  :rtype: int
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
  Main function to display the GUI and start monitoring the directory for changes.
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

