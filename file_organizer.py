import datetime
import os
import shutil
import argparse


def extract_name_from_filename(filename):
    name_without_ext = os.path.splitext(filename)[0]
    parts = name_without_ext.split("-")
    if len(parts) >= 2:
        return parts[-1].strip()
    return None


def organize_files(source_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for root, _, files in os.walk(source_dir):
        for filename in files:
            source_path = os.path.join(root, filename)
            try:
                name = extract_name_from_filename(filename)
                if not name:
                    continue
                dest_folder = os.path.join(output_dir, name)
                os.makedirs(dest_folder, exist_ok=True)
                dest_path = os.path.join(dest_folder, filename)
                shutil.move(source_path, dest_path)
            except Exception as e:
                print(f"❌ Error: {filename} - {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Organize files into folders based on name pattern (xxx-Name.ext)"
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input directory containing files to organize",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="organized_output",
        required=False,
        help="Output directory where organized folders will be created",
    )

    args = parser.parse_args()

    source_dir = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output)

    if not os.path.exists(source_dir):
        print(f"❌ source directory does not exist: {source_dir}")
        return

    organize_files(source_dir, output_dir)


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print(f"file_organizer: 🚀 starting process at {start_time}")

    main()

    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    print(f"file_organizer: ✅  execution finished. Total time: {total_time}")
