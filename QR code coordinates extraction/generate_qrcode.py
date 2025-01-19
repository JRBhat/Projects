import qrcode
import os

def make_quick_qrcode(text: str, path_to_save: str) -> None:
    """
    Generates a basic QR code from the provided text and saves it to the specified path.

    :param text: The text or data to be encoded into the QR code.
    :type text: str
    :param path_to_save: The full path where the generated QR code will be saved.
    :type path_to_save: str
    :return: None
    """
    img = qrcode.make(text)

    print(type(img))
    print(img.size)
    img.save(path_to_save)  # overwrites existing image1.png
    print(f"QR code updated with {text}")
    # input("Press enter to continue...")

def make_custom_qrcode(
    text: str, 
    path_to_save: str, 
    box_size: int = 8, 
    border: int = 4, 
    fill_color: str = "darkgreen",  
    back_color: str = "#ffffff"
) -> None:
    """
    Generates a custom QR code from the provided text with customizable design options 
    and saves it to the specified path.

    :param text: The text or data to be encoded into the QR code.
    :type text: str
    :param path_to_save: The directory path where the generated QR code will be saved.
    :type path_to_save: str
    :param box_size: The size of each box in the QR code grid, defaults to 8.
    :type box_size: int, optional
    :param border: The thickness of the border around the QR code, defaults to 4.
    :type border: int, optional
    :param fill_color: The color of the QR code modules, defaults to "darkgreen".
    :type fill_color: str, optional
    :param back_color: The background color of the QR code, defaults to "#ffffff".
    :type back_color: str, optional
    :return: None
    """
    qr = qrcode.QRCode(
        version=12,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border
    )
    
    qr.add_data(text)
    qr.make()
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    img.save(os.path.join(path_to_save, f"qrcode_test_custom{fill_color}.png"))

def main() -> None:
    """
    Main function to demonstrate QR code generation.

    :return: None
    """
    PATH_TO_SAVE = r"D:\Code\Codebase_Bha\Dev_Project22_QRCode_reader_coordnates_extraction\bin\test\pos_qrcodes\pos3.png"
    TEXT = """Pos 3"""
    
    make_quick_qrcode(TEXT, PATH_TO_SAVE)
    # make_custom_qrcode(TEXT, PATH_TO_SAVE, fill_color="darkred")

if __name__ == '__main__':
    main()
