import os
import cv2

from src.modules.sensitive_data_masker.matcher import (
    load_coordinate_templates,
    find_matching_template,
    scale_coordinates,
)
from src.modules.sensitive_data_masker.masking import (
    apply_mask_to_image,
    apply_mask_to_pdf,
    generate_output_path,
)
from src.utils.mime_type import get_mime_type


def process_file_with_templates(file_path: str, templates: dict, output_dir: str):
    """
    Process a single file: find matching template and apply masking

    Args:
        file_path: Path to the file to process
        templates: Dictionary of coordinate templates
        output_dir: Output directory for masked files

    Returns:
        dict: Result with 'path', 'status', 'bank', 'template', 'similarity'
    """
    try:
        # Find matching template using Gemini AI with 85% confidence threshold
        match = find_matching_template(file_path, templates, threshold=0.85)

        if not match:
            return {
                "path": file_path,
                "status": "no_match",
                "bank": None,
                "template": None,
                "similarity": 0,
            }

        # Get coordinates from template
        template_coords = match["template"]["coordinates"]

        # Load input image to get dimensions
        input_image = cv2.imread(file_path)
        if input_image is None:
            return {
                "path": file_path,
                "status": "error",
                "error": "Could not load image",
                "bank": match["bank"],
                "template": match["template"]["name"],
                "similarity": match["similarity"],
            }

        # Get dimensions
        input_height, input_width = input_image.shape[:2]
        ref_image = match["template"]["reference_image"]
        ref_height, ref_width = ref_image.shape[:2]

        # Scale coordinates if dimensions differ
        if input_width != ref_width or input_height != ref_height:
            coordinates = scale_coordinates(
                template_coords, ref_width, ref_height, input_width, input_height
            )
            print(
                f"   📏 Scaled coordinates from {ref_width}x{ref_height} to {input_width}x{input_height}"
            )
        else:
            coordinates = template_coords

        # Generate output path
        output_path = generate_output_path(file_path, output_dir)

        # Apply masking based on file type
        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()

        success = False
        if ext_lower in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]:
            success = apply_mask_to_image(file_path, coordinates, output_path)
        elif ext_lower == ".pdf":
            success = apply_mask_to_pdf(file_path, coordinates, output_path)

        if success:
            print(f"   ✅ Masked file saved to: {output_path}")
            return {
                "path": file_path,
                "status": "success",
                "bank": match["bank"],
                "template": match["template"]["name"],
                "similarity": match["similarity"],
                "output_path": output_path,
            }
        else:
            return {
                "path": file_path,
                "status": "error",
                "error": "Masking failed",
                "bank": match["bank"],
                "template": match["template"]["name"],
                "similarity": match["similarity"],
            }

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return {"path": file_path, "status": "error", "error": str(e)}


async def process_files_with_coordinate_matching(real_path: str, output_dir: str):
    """
    Process all files in a directory using coordinate template matching

    Args:
        real_path: Path to directory containing files to process
        output_dir: Output directory for masked files

    Returns:
        dict: Statistics about the processing
    """
    print("\n📂 Loading coordinate templates...")
    templates = load_coordinate_templates()

    if not templates:
        print("❌ No coordinate templates found!")
        return {"total": 0, "success": 0, "no_match": 0, "error": 0}

    results = []
    stats = {"total": 0, "success": 0, "no_match": 0, "error": 0}

    print(f"\n🔍 Processing files from: {real_path}\n")

    # Process all files in directory
    for root, _, files in os.walk(real_path, followlinks=True):
        for file in files:
            mime_type = get_mime_type(file)

            if not mime_type:
                continue

            file_path = os.path.join(root, file)
            stats["total"] += 1

            print(f"\n📄 Processing: {os.path.basename(file_path)}")
            result = process_file_with_templates(file_path, templates, output_dir)
            results.append(result)

            # Update stats
            stats[result["status"]] += 1

    return stats
