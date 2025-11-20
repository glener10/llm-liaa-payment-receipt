import os
from PIL import Image, ImageDraw
import fitz


def apply_mask_to_image(image_path, coordinates, output_path):
    """
    Applies black masks to an image at specified coordinates

    Args:
        image_path: Path to the original image
        coordinates: List of dicts with x, y, width, height
        output_path: Path where the masked image will be saved

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        for coord in coordinates:
            x = coord["x"]
            y = coord["y"]
            width = coord["width"]
            height = coord["height"]

            draw.rectangle([x, y, x + width, y + height], fill="black")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)

        return True

    except Exception as e:
        print(f"❌ Error masking image {image_path}: {e}")
        return False


def apply_mask_to_pdf(pdf_path, coordinates, output_path):
    """
    Applies black masks to a PDF at specified coordinates

    Args:
        pdf_path: Path to the original PDF
        coordinates: List of dicts with x, y, width, height
        output_path: Path where the masked PDF will be saved

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        doc = fitz.open(pdf_path)

        for page in doc:
            for coord in coordinates:
                x = coord["x"]
                y = coord["y"]
                width = coord["width"]
                height = coord["height"]

                rect = fitz.Rect(x, y, x + width, y + height)
                page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        doc.close()

        return True
    except Exception as e:
        print(f"❌ Error masking PDF {pdf_path}: {e}")
        return False


def generate_output_path(original_path, output_dir):
    """
    Generates output path maintaining the directory structure

    Args:
        original_path: Original file path
        output_dir: Base output directory

    Returns:
        str: New path for the masked file
    """
    filename = os.path.basename(original_path)
    name, ext = os.path.splitext(filename)

    masked_filename = f"{name}_masked{ext}"
    output_path = os.path.join(output_dir, masked_filename)

    return output_path
