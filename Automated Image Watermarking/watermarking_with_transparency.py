from PIL import Image
import os
from typing import Union

def watermark_image_center(input_image_path: str, output_image_path: str, watermark_image_path: str, alpha: float) -> None:
    """
    Watermarks the center of an image with a semi-transparent watermark.

    :param input_image_path: Path to the input image.
    :param output_image_path: Path to save the output image.
    :param watermark_image_path: Path to the watermark image.
    :param alpha: Transparency level of the watermark (0 to 1).
    """
    photo = Image.open(input_image_path)
    watermark = Image.open(watermark_image_path)
    photo_width, photo_height = photo.size
    watermark = watermark.resize((500, 500), Image.Resampling.LANCZOS)
    watermark_width, watermark_height = watermark.size

    layer = Image.new('RGBA', photo.size, (0, 0, 0, 0))
    watermark_position = ((photo_width - watermark_width) // 2, (photo_height - watermark_height) // 2)
    layer.paste(watermark, watermark_position)

    alpha_layer = layer.copy()
    alpha_layer.putalpha(int(alpha * 255))
    layer = Image.alpha_composite(photo.convert('RGBA'), alpha_layer)

    layer.convert(photo.mode).save(output_image_path)

def watermark_image_corners(input_image_path: str, output_image_path: str, watermark_image_path: str, alpha: float) -> None:
    """
    Watermarks the bottom-right corner of an image with a semi-transparent watermark.

    :param input_image_path: Path to the input image.
    :param output_image_path: Path to save the output image.
    :param watermark_image_path: Path to the watermark image.
    :param alpha: Transparency level of the watermark (0 to 1).
    """
    photo = Image.open(input_image_path)
    watermark = Image.open(watermark_image_path)
    photo_width, photo_height = photo.size
    watermark = watermark.resize((100, 100), Image.Resampling.LANCZOS)
    watermark_width, watermark_height = watermark.size

    layer = Image.new('RGBA', photo.size, (0, 0, 0, 0))
    watermark_position = (photo_width - watermark_width, photo_height - watermark_height)
    layer.paste(watermark, watermark_position)

    alpha_layer = layer.copy()
    alpha_layer.putalpha(int(alpha * 255))
    layer = Image.alpha_composite(photo.convert('RGBA'), alpha_layer)

    layer.convert(photo.mode).save(output_image_path)

if __name__ == '__main__':
    img_inp_path = r"path to images to be watermarked"
    img_output_path = os.path.join(img_inp_path, "watermarked_copyright")
    if not os.path.exists(img_output_path):
        os.mkdir(img_output_path)

    for img in os.listdir(img_inp_path):
        watermark_image_center(os.path.join(img_inp_path, img), os.path.join(img_output_path, img.replace(".png", "_output.png")), r"C:\Users\JBhat\Documents\copyright_v2.png", 0.05)
