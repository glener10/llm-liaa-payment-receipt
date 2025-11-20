import os
from PIL import Image, ImageDraw
import fitz


def apply_mask_to_image(image_path, coordinates, output_path):
    """
    Applies black masks to an image at specified coordinates

    Args:
        image_path: Path to the original image
        coordinates: List of dicts with 'field' and 'coordinates' (x, y, width, height)
        output_path: Path where the masked image will be saved

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        for field in coordinates:
            coord = field["coordinates"]
            x = coord["x"]
            y = coord["y"]
            width = coord["width"]
            height = coord["height"]

            draw.rectangle([x, y, x + width, y + height], fill="black")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)

        return True

    except Exception as e:
        print(f"error masking image {image_path}: {e}")
        return False


def apply_mask_to_pdf(pdf_path, coordinates, output_path):
    """
    Applies black masks to a PDF at specified coordinates

    Args:
        pdf_path: Path to the original PDF
        coordinates: List of dicts with 'field' and 'coordinates' (x, y, width, height)
        output_path: Path where the masked PDF will be saved

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        doc = fitz.open(pdf_path)

        for page in doc:
            for field in coordinates:
                coord = field["coordinates"]
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
        print(f"error masking PDF {pdf_path}: {e}")
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


def apply_masks_to_files(validated_results, output_dir):
    """
    Applies masks to all validated files

    Args:
        validated_results: List of dicts with 'path' and 'coordinates'
        output_dir: Directory where masked files will be saved

    Returns:
        dict: Statistics about the masking process
    """
    stats = {"total": len(validated_results), "success": 0, "failed": 0, "skipped": 0}

    for result in validated_results:
        file_path = result["path"]
        coordinates = result["coordinates"]

        if not coordinates or len(coordinates) == 0:
            stats["skipped"] += 1
            continue

        output_path = generate_output_path(file_path, output_dir)

        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()

        success = False

        if ext_lower in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]:
            success = apply_mask_to_image(file_path, coordinates, output_path)
        elif ext_lower == ".pdf":
            success = apply_mask_to_pdf(file_path, coordinates, output_path)
        else:
            stats["skipped"] += 1
            continue

        if success:
            stats["success"] += 1
        else:
            stats["failed"] += 1

    return stats
