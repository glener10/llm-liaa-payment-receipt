import os
import pathlib

from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

from src.modules.classify.prompt import get_prompt_find_out_bank_of_payment_receipts
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
prompt = get_prompt_find_out_bank_of_payment_receipts()


async def get_bank_of_receipt(file_path: str, mime_type: str) -> str:
    try:
        contents = [prompt]
        filepath = pathlib.Path(file_path)
        contents.append({"mime_type": mime_type, "data": filepath.read_bytes()})

        response = await gemini_client.generate_content_async(contents=contents)

        return {"classify": response.text, "path": file_path}
    except Exception as e:
        print(f"get_bank_of_receipt - error in {file_path}: {e}")
        return {"classify": None, "path": file_path}


def get_promises_of_all_files_to_find_out_bank_of_payment_receipts(real_path: str):
    tasks = []
    try:
        for root, _, files in os.walk(real_path, followlinks=True):
            for file in files:
                mime_type = get_mime_type(file)

                if not mime_type:
                    print(
                        f"get_promises_of_all_files_to_find_out_bank_of_payment_receipts file {file} without extension in {root}"
                    )
                    continue

                all_path = os.path.join(root, file)
                gemini_classify_task = get_bank_of_receipt(
                    file_path=all_path,
                    mime_type=mime_type,
                )
                tasks.append(gemini_classify_task)
        return tasks
    except Exception as e:
        print(
            f"get_promises_of_all_files_to_find_out_bank_of_payment_receipts - error: {e}"
        )
        raise e
