import datetime
import argparse
import os
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

from src.utils.dirs import remove_empty_dirs

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)
gemini_client = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=types.GenerationConfig(
        response_mime_type="application/json",
    ),
)


def check_sensitive_data(file_path):
    """
    Check if file contains visible sensitive data using Gemini

    Returns:
        dict: {'has_sensitive_data': bool, 'reason': str}
    """
    try:
        prompt = """Analise esta imagem de comprovante bancário e verifique se há DADOS SENSÍVEIS VISÍVEIS.

Dados sensíveis incluem:
- Nome completo de pessoas
- CPF
- Chave Pix (CPF, email, telefone, chave aleatória)
- Número de conta bancária
- Agência
- Identificador da transação

Retorne um JSON com:
{
    "has_sensitive_data": true/false,
    "reason": "explicação do que foi encontrado ou confirmação de que tudo está mascarado"
}

Se TODOS os dados sensíveis estiverem cobertos por tarjas pretas, retorne has_sensitive_data=false.
Se QUALQUER dado sensível estiver visível, retorne has_sensitive_data=true."""

        with open(file_path, "rb") as f:
            file_data = f.read()

        file_ext = Path(file_path).suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".pdf": "application/pdf",
        }
        mime_type = mime_map.get(file_ext, "image/jpeg")

        contents = [prompt, {"mime_type": mime_type, "data": file_data}]

        response = gemini_client.generate_content(contents=contents)
        result = json.loads(response.text)
        return result

    except Exception as e:
        return {
            "has_sensitive_data": True,
            "reason": f"Error during check: {str(e)}",
        }


def process_files(input_dir, output_dir):
    """
    Process all files in input directory and validate masking

    Args:
        input_dir: Directory with masked files to validate
        output_dir: Directory to copy files that passed validation

    Returns:
        dict: Statistics about the validation
    """
    for root, _, files in os.walk(input_dir):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() not in [
                ".png",
                ".jpg",
                ".jpeg",
                ".pdf",
            ]:
                continue

            file_path = os.path.join(root, file)

            rel_path = os.path.relpath(file_path, input_dir)

            print(f"guardrails: validating '{rel_path}' 🔍")
            result = check_sensitive_data(file_path)

            if result["has_sensitive_data"]:
                print(
                    f"guardrails: '{rel_path}' sensitive data found - {result['reason']} ⚠️"
                )
            else:
                output_file_path = os.path.join(output_dir, rel_path)
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                shutil.move(file_path, output_file_path)
                print(
                    f"guardrails: '{rel_path}' all data masked - {result['reason']} ✅"
                )


def main():
    parser = argparse.ArgumentParser(
        description="Validate masked files for sensitive data"
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Directory containing masked files to validate",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Directory to copy files that passed validation",
    )

    args = parser.parse_args()

    input_dir = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output)

    if not os.path.exists(input_dir):
        print(f"guardrails: ❌ Input directory does not exist: {input_dir}")
        return

    os.makedirs(output_dir, exist_ok=True)

    process_files(input_dir, output_dir)
    remove_empty_dirs(input_dir)


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print(f"guardrails: 🚀 Starting guardrails validation at {start_time}")

    main()

    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    print(f"guardrails: ✅  Execution finished. Total time: {total_time}")
