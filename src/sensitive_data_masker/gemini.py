import os
import pathlib

from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types
from PIL import Image
import fitz

from src.sensitive_data_masker.prompt import get_prompt_sensitive_data_masker
from src.utils.mime_type import get_mime_type

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)
gemini_client = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=types.GenerationConfig(
        response_mime_type="text/plain",
    ),
)


def get_file_dimensions(file_path: str, mime_type: str):
    """
    Get the dimensions of an image or PDF file

    Args:
        file_path: Path to the file
        mime_type: MIME type of the file

    Returns:
        tuple: (width, height) in pixels, or (None, None) if unable to determine
    """
    try:
        if mime_type.startswith("image/"):
            with Image.open(file_path) as img:
                return img.size  # Returns (width, height)
        elif mime_type == "application/pdf":
            doc = fitz.open(file_path)
            if len(doc) > 0:
                page = doc[0]
                rect = page.rect
                doc.close()
                return (int(rect.width), int(rect.height))
            doc.close()
    except Exception as e:
        print(f"Warning: Could not get dimensions for {file_path}: {e}")

    return (None, None)


async def get_coordinates_to_mask(file_path: str, mime_type: str) -> str:
    try:
        width, height = get_file_dimensions(file_path, mime_type)
        prompt = get_prompt_sensitive_data_masker(width, height)

        contents = [prompt]
        filepath = pathlib.Path(file_path)
        contents.append({"mime_type": mime_type, "data": filepath.read_bytes()})

        response = await gemini_client.generate_content_async(contents=contents)

        return {"coordinates": response.text, "path": file_path}
    except Exception as e:
        print(f"get_coordinates_to_mask - error in {file_path}: {e}")
        return {"coordinates": None, "path": file_path}


def get_promises_of_all_files_to_mask_sensitive_data(real_path: str):
    tasks = []
    try:
        for root, _, files in os.walk(real_path, followlinks=True):
            for file in files:
                mime_type = get_mime_type(file)

                if not mime_type:
                    print(
                        f"get_promises_of_all_files_to_mask_sensitive_data file {file} without extension in {root}"
                    )
                    continue

                all_path = os.path.join(root, file)
                gemini_mask_task = get_coordinates_to_mask(
                    file_path=all_path,
                    mime_type=mime_type,
                )
                tasks.append(gemini_mask_task)
        return tasks
    except Exception as e:
        print(f"get_promises_of_all_files_to_mask_sensitive_data - error: {e}")
        raise e
