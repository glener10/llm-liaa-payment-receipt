import asyncio
import datetime
import os

from src.classify.output import move_files_to_specified_bank_folders
from src.classify.gemini import (
    get_promises_of_all_files_to_find_out_bank_of_payment_receipts,
)
from src.classify.args import get_args


async def main():
    args = get_args()
    real_path = os.path.realpath(args.path)

    print("preparing promises of all files")
    all_files_promises = get_promises_of_all_files_to_find_out_bank_of_payment_receipts(
        real_path
    )
    print(
        "executing all promises to find out which bank each payment receipt belongs to"
    )
    results_from_models = await asyncio.gather(*all_files_promises)

    print("moving files to")
    move_files_to_specified_bank_folders(results_from_models, args.output)

    print(f"\nclassification successfully completed in the folder '{args.output}'")


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print(f"🚀 starting process at {start_time}")

    asyncio.run(main())

    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    print(f"⏱️  execution finished. Total time: {total_time}")
