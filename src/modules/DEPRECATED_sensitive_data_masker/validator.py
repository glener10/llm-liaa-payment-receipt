import json


def clean_json_response(response_text):
    if not response_text or not isinstance(response_text, str):
        return None

    cleaned = response_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    return cleaned


def validate_coordinate_object(coord):
    required_fields = ["x", "y", "width", "height"]

    if not isinstance(coord, dict):
        return False

    for field in required_fields:
        if field not in coord:
            return False
        if not isinstance(coord[field], (int, float)):
            return False

    return True


def validate_field_object(field_obj):
    if not isinstance(field_obj, dict):
        return False

    if "field" not in field_obj or "coordinates" not in field_obj:
        return False

    if not isinstance(field_obj["field"], str):
        return False

    return validate_coordinate_object(field_obj["coordinates"])


def parse_ai_response(response_text):
    try:
        cleaned_text = clean_json_response(response_text)

        if not cleaned_text:
            return None

        data = json.loads(cleaned_text)

        if not isinstance(data, list):
            return None

        for item in data:
            if not validate_field_object(item):
                return None

        return data

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return None
    except Exception as e:
        print(f"Validation error: {e}")
        return None


def validate_and_clean_results(results_from_models):
    validated_results = []

    for result in results_from_models:
        if not isinstance(result, dict):
            print(f"Invalid result format: expected dict, got {type(result)}")
            continue

        if "coordinates" not in result or "path" not in result:
            print(f"Missing required keys in result: {result.keys()}")
            continue

        parsed_coordinates = parse_ai_response(result["coordinates"])

        if parsed_coordinates is None:
            print(f"Failed to parse coordinates for file: {result['path']}")
            continue

        validated_results.append(
            {"coordinates": parsed_coordinates, "path": result["path"]}
        )

    return validated_results
