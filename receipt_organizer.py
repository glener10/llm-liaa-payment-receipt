import asyncio
import datetime
import os

from src.modules.classify.output import move_files_to_specified_bank_folders
from src.modules.classify.gemini import (
    get_promises_of_all_files_to_find_out_bank_of_payment_receipts,
)
from src.modules.classify.args import get_args


async def main():
    args = get_args()
    real_path = os.path.realpath(args.input)

    all_files_promises = get_promises_of_all_files_to_find_out_bank_of_payment_receipts(
        real_path
    )
    print(
        "receipt_organizer: executing all promises to find out which bank each payment receipt belongs to"
    )
    results_from_models = await asyncio.gather(*all_files_promises)

    print("receipt_organizer: moving files to")
    move_files_to_specified_bank_folders(results_from_models, args.output)


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print(f"receipt_organizer: 🚀 starting process at {start_time}")

    asyncio.run(main())

    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    print(f"receipt_organizer: ✅  execution finished. Total time: {total_time}")
