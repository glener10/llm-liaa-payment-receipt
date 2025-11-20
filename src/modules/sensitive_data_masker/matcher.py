import os
import json
import cv2
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)
gemini_client = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=types.GenerationConfig(
        response_mime_type="application/json",
    ),
)


def compare_images_with_gemini(img1_path, img2_path, bank_name, template_name):
    """
    Use Gemini to compare if two images have the same layout/format

    Args:
        img1_path: Path to reference image (with masks)
        img2_path: Path to input image (to compare)
        bank_name: Name of the bank
        template_name: Name of the template

    Returns:
        dict: {'is_match': bool, 'confidence': float, 'reason': str}
    """
    try:
        prompt = f"""Você é um especialista em análise de documentos bancários.

Analise as duas imagens fornecidas e determine se elas têm o MESMO FORMATO/LAYOUT de comprovante bancário.

IMPORTANTE:
- A primeira imagem (referência) pode ter dados mascarados com tarjas pretas - IGNORE essas tarjas
- Compare apenas a ESTRUTURA, LAYOUT e FORMATO do documento
- Verifique se são do mesmo banco/instituição financeira
- Verifique se têm a mesma disposição de elementos (cabeçalho, campos, rodapé)
- Os VALORES dos dados podem ser diferentes (nomes, valores, datas) - isso é NORMAL
- Foque na similaridade do DESIGN e ESTRUTURA

Informações de contexto:
- Banco esperado: {bank_name}
- Template: {template_name}

Retorne um JSON com:
{{
    "is_match": true/false,
    "confidence": 0.0-1.0,
    "reason": "explicação detalhada da decisão",
    "bank_detected": "nome do banco detectado na imagem de input",
    "layout_elements": ["elemento1", "elemento2", ...] elementos de layout detectados
}}

Seja rigoroso: apenas retorne is_match=true se tiver alta confiança (>85%) de que são do mesmo formato."""

        # Read images as bytes
        with open(img1_path, "rb") as f:
            img1_data = f.read()
        with open(img2_path, "rb") as f:
            img2_data = f.read()

        # Determine mime types
        img1_ext = Path(img1_path).suffix.lower()
        img2_ext = Path(img2_path).suffix.lower()

        mime_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }

        img1_mime = mime_type_map.get(img1_ext, "image/jpeg")
        img2_mime = mime_type_map.get(img2_ext, "image/jpeg")

        # Prepare content for Gemini
        contents = [
            prompt,
            {"mime_type": img1_mime, "data": img1_data},
            {"mime_type": img2_mime, "data": img2_data},
        ]

        response = gemini_client.generate_content(contents=contents)
        result = json.loads(response.text)

        return result

    except Exception as e:
        print(f"⚠️  Error comparing with Gemini: {e}")
        import traceback

        traceback.print_exc()
        return {
            "is_match": False,
            "confidence": 0.0,
            "reason": f"Error: {str(e)}",
            "bank_detected": "unknown",
            "layout_elements": [],
        }


def load_coordinate_templates(coordinates_dir="src/config/coordinates"):
    """
    Load all coordinate templates from the config directory

    Returns:
        dict: Dictionary with bank names as keys and list of templates as values
        Each template contains: {
            'name': str,
            'reference_image_path': str,
            'coordinates': list,
            'reference_image': numpy array
        }
    """
    templates = {}

    if not os.path.exists(coordinates_dir):
        print(f"⚠️  Coordinates directory not found: {coordinates_dir}")
        return templates

    # Iterate through each bank directory
    for bank_name in os.listdir(coordinates_dir):
        bank_dir = os.path.join(coordinates_dir, bank_name)

        if not os.path.isdir(bank_dir):
            continue

        templates[bank_name] = []

        # Find all coordinate JSON files
        json_files = [f for f in os.listdir(bank_dir) if f.endswith(".json")]

        for json_file in json_files:
            # Get the base name (e.g., coordinates_output_a)
            base_name = json_file.replace(".json", "")
            png_file = f"{base_name}.png"

            json_path = os.path.join(bank_dir, json_file)
            png_path = os.path.join(bank_dir, png_file)

            # Check if corresponding PNG exists
            if not os.path.exists(png_path):
                print(f"⚠️  Missing reference image: {png_path}")
                continue

            # Load coordinates
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    coordinates = json.load(f)

                # Load reference image
                reference_image = cv2.imread(png_path)

                if reference_image is None:
                    print(f"⚠️  Could not load reference image: {png_path}")
                    continue

                templates[bank_name].append(
                    {
                        "name": base_name,
                        "reference_image_path": png_path,
                        "coordinates": coordinates,
                        "reference_image": reference_image,
                    }
                )

            except Exception as e:
                print(f"❌ Error loading template {json_file}: {e}")
                continue

        if templates[bank_name]:
            print(
                f"📂 Loaded {len(templates[bank_name])} template(s) for '{bank_name}'"
            )

    return templates


def create_mask_from_black_regions(img, threshold=30):
    """
    Create a mask to identify black/masked regions in an image

    Args:
        img: Input image (BGR)
        threshold: Threshold for considering a pixel as black (0-255)

    Returns:
        numpy array: Binary mask where 1 = valid region, 0 = masked region
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Create mask where black regions (masked data) are marked as 0
    # Non-black regions are marked as 1
    mask = (gray > threshold).astype(np.uint8)

    # Dilate the black regions slightly to include edges
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)

    return mask


def compare_images_structure(img1, img2, threshold=0.85):
    """
    Compare two images to see if they have the same structure/layout
    Ignores masked (black) regions in the reference image

    Args:
        img1: First image (numpy array) - reference with masks
        img2: Second image (numpy array) - input to compare
        threshold: Similarity threshold (0-1)

    Returns:
        float: Similarity score (0-1), or 0 if comparison fails
    """
    try:
        # Resize images to same size for comparison
        height = min(img1.shape[0], img2.shape[0])
        width = min(img1.shape[1], img2.shape[1])

        img1_resized = cv2.resize(img1, (width, height))
        img2_resized = cv2.resize(img2, (width, height))

        # Create mask to ignore black regions in reference image
        valid_mask = create_mask_from_black_regions(img1_resized)

        # Convert to grayscale
        gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)

        # Apply mask to both images
        gray1_masked = gray1 * valid_mask
        gray2_masked = gray2 * valid_mask

        # 1. HISTOGRAM COMPARISON on non-masked regions (weighted 20%)
        hist1 = cv2.calcHist([gray1_masked], [0], valid_mask * 255, [256], [0, 256])
        hist2 = cv2.calcHist([gray2_masked], [0], valid_mask * 255, [256], [0, 256])
        cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        hist_similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

        # 2. EDGE DETECTION - Structure similarity on non-masked regions (weighted 35%)
        edges1 = cv2.Canny(gray1, 50, 150)
        edges2 = cv2.Canny(gray2, 50, 150)

        # Apply mask to edges
        edges1_masked = edges1 * valid_mask
        edges2_masked = edges2 * valid_mask

        edge_diff = cv2.absdiff(edges1_masked, edges2_masked)
        valid_pixels = np.sum(valid_mask)
        if valid_pixels > 0:
            edge_similarity = 1 - (np.sum(edge_diff) / (valid_pixels * 255))
        else:
            edge_similarity = 0

        # 3. STRUCTURAL SIMILARITY using correlation on grid (weighted 25%)
        grid_rows, grid_cols = 4, 3
        h_step = height // grid_rows
        w_step = width // grid_cols

        grid_similarities = []
        for i in range(grid_rows):
            for j in range(grid_cols):
                y1, y2 = i * h_step, (i + 1) * h_step
                x1, x2 = j * w_step, (j + 1) * w_step

                region1 = gray1[y1:y2, x1:x2]
                region2 = gray2[y1:y2, x1:x2]
                region_mask = valid_mask[y1:y2, x1:x2]

                # Only compare if there's significant valid area in this region
                if np.sum(region_mask) > (region_mask.size * 0.3):
                    # Apply mask
                    region1_masked = region1 * region_mask
                    region2_masked = region2 * region_mask

                    # Calculate correlation on masked regions
                    if region1_masked.size > 0 and region2_masked.size > 0:
                        # Flatten and remove zeros
                        r1_flat = region1_masked[region_mask > 0].flatten()
                        r2_flat = region2_masked[region_mask > 0].flatten()

                        if len(r1_flat) > 10 and len(r2_flat) > 10:
                            correlation = np.corrcoef(r1_flat, r2_flat)[0, 1]
                            if not np.isnan(correlation):
                                grid_similarities.append(max(0, correlation))

        grid_similarity = np.mean(grid_similarities) if grid_similarities else 0

        # 4. COLOR HISTOGRAM COMPARISON on valid regions (weighted 10%)
        hsv1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2HSV)

        hist_h1 = cv2.calcHist([hsv1], [0], valid_mask * 255, [50], [0, 180])
        hist_h2 = cv2.calcHist([hsv2], [0], valid_mask * 255, [50], [0, 180])
        cv2.normalize(hist_h1, hist_h1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(hist_h2, hist_h2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        color_similarity = cv2.compareHist(hist_h1, hist_h2, cv2.HISTCMP_CORREL)

        # 5. LAYOUT STRUCTURE - Compare positions of text/content blocks (weighted 10%)
        # Use adaptive thresholding to find text regions
        thresh1 = cv2.adaptiveThreshold(
            gray1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        thresh2 = cv2.adaptiveThreshold(
            gray2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Apply mask
        thresh1_masked = thresh1 * valid_mask
        thresh2_masked = thresh2 * valid_mask

        # Compare layout structure
        if valid_pixels > 0:
            layout_diff = cv2.absdiff(thresh1_masked, thresh2_masked)
            layout_similarity = 1 - (np.sum(layout_diff) / (valid_pixels * 255))
        else:
            layout_similarity = 0

        # WEIGHTED COMBINATION
        combined_similarity = (
            hist_similarity * 0.20
            + edge_similarity * 0.35
            + grid_similarity * 0.25
            + color_similarity * 0.10
            + layout_similarity * 0.10
        )

        # Normalize to [0, 1] range
        combined_similarity = max(0, min(1, combined_similarity))

        return combined_similarity

    except Exception as e:
        print(f"⚠️  Error comparing images: {e}")
        import traceback

        traceback.print_exc()
        return 0


def find_matching_template(file_path, templates, threshold=0.85):
    """
    Find the best matching template for a given file using Gemini AI

    Args:
        file_path: Path to the input file
        templates: Dictionary of templates from load_coordinate_templates
        threshold: Minimum confidence threshold (default: 0.85)

    Returns:
        dict or None: Matching template with 'bank', 'template', 'similarity' and 'reason' keys
    """
    try:
        best_match = None
        best_confidence = 0
        all_matches = []

        print("   🤖 Comparing with Gemini AI...")

        # Compare against all templates using Gemini
        for bank_name, bank_templates in templates.items():
            for template in bank_templates:
                print(f"      🔍 Checking {bank_name}/{template['name']}...")

                result = compare_images_with_gemini(
                    template["reference_image_path"],
                    file_path,
                    bank_name,
                    template["name"],
                )

                confidence = result.get("confidence", 0.0)
                is_match = result.get("is_match", False)

                all_matches.append(
                    {
                        "bank": bank_name,
                        "template": template,
                        "confidence": confidence,
                        "is_match": is_match,
                        "reason": result.get("reason", ""),
                        "bank_detected": result.get("bank_detected", "unknown"),
                    }
                )

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = {
                        "bank": bank_name,
                        "template": template,
                        "similarity": confidence,
                        "is_match": is_match,
                        "reason": result.get("reason", ""),
                        "bank_detected": result.get("bank_detected", "unknown"),
                    }

        # Show all candidates for debugging
        if all_matches:
            print("   📊 Gemini Analysis Results:")
            for match in sorted(
                all_matches, key=lambda x: x["confidence"], reverse=True
            ):
                status = (
                    "✅"
                    if match["is_match"] and match["confidence"] >= threshold
                    else "❌"
                )
                print(
                    f"      {status} {match['bank']}/{match['template']['name']}: "
                    f"{match['confidence']:.0%} confidence"
                )
                print(f"         Bank detected: {match['bank_detected']}")
                print(f"         Reason: {match['reason'][:100]}...")

        # Check if we have a valid match
        if best_match and best_match["is_match"] and best_confidence >= threshold:
            print(
                f"   ✅ MATCH CONFIRMED: {best_match['bank']}/{best_match['template']['name']} "
                f"(confidence: {best_confidence:.0%})"
            )
            print(f"      Reason: {best_match['reason']}")
            return best_match
        else:
            print(
                f"   ❌ NO MATCH: Best confidence was {best_confidence:.0%} (threshold: {threshold:.0%})"
            )
            if best_match:
                print(f"      Reason: {best_match['reason']}")
            return None

    except Exception as e:
        print(f"❌ Error finding matching template: {e}")
        import traceback

        traceback.print_exc()
        return None


def scale_coordinates(
    coordinates, source_width, source_height, target_width, target_height
):
    """
    Scale coordinates from source dimensions to target dimensions

    Args:
        coordinates: List of coordinate dicts with x, y, width, height
        source_width: Width of the reference image
        source_height: Height of the reference image
        target_width: Width of the target image
        target_height: Height of the target image

    Returns:
        list: Scaled coordinates
    """
    scale_x = target_width / source_width
    scale_y = target_height / source_height

    scaled_coords = []
    for coord in coordinates:
        scaled_coords.append(
            {
                "x": int(coord["x"] * scale_x),
                "y": int(coord["y"] * scale_y),
                "width": int(coord["width"] * scale_x),
                "height": int(coord["height"] * scale_y),
            }
        )

    return scaled_coords
