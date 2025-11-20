import datetime
import subprocess
import argparse
import os
import shutil

from src.utils.dirs import remove_empty_dirs


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline: organize files by name, then classify by bank"
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
        required=True,
        help="Output directory for organized and classified files",
    )

    args = parser.parse_args()

    temp_organized = "z_temp_organized"

    print(
        f"pipeline: executing file_organizer.py to organize files {args.input} into {temp_organized}"
    )
    subprocess.run(
        f"python file_organizer.py -i '{args.input}' -o '{temp_organized}'",
        shell=True,
        check=True,
    )

    for person_folder in os.listdir(temp_organized):
        person_path = os.path.join(temp_organized, person_folder)
        if os.path.isdir(person_path):
            output_person_path = os.path.join(args.output, person_folder)
            print(
                f"pipeline: executing receipt_organizer.py to organize files {person_path} into {output_person_path}"
            )
            subprocess.run(
                f"python receipt_organizer.py -i '{person_path}' -o '{output_person_path}'",
                shell=True,
                check=True,
            )

    print(f"pipeline: cleaning up temporary directory {temp_organized}")
    remove_empty_dirs(temp_organized)
    shutil.rmtree(temp_organized)


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print(f"pipeline: 🚀 starting process at {start_time}")

    main()

    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    print(f"pipeline: ✅  execution finished. Total time: {total_time}")
