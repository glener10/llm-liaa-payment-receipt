import asyncio
import datetime
import os

from src.modules.DEPRECATED_sensitive_data_masker.gemini import (
    get_promises_of_all_files_to_mask_sensitive_data,
)
from src.modules.DEPRECATED_sensitive_data_masker.args import get_args
from src.modules.DEPRECATED_sensitive_data_masker.validator import (
    validate_and_clean_results,
)
from src.modules.DEPRECATED_sensitive_data_masker.masking import apply_masks_to_files


async def main():
    args = get_args()
    real_path = os.path.realpath(args.path)
    output_dir = os.path.abspath(args.output)

    print("preparing promises of all files")
    all_files_promises = get_promises_of_all_files_to_mask_sensitive_data(real_path)
    print("executing all promises...")
    results_from_models = await asyncio.gather(*all_files_promises)

    print("\nvalidating and cleaning results...")
    validated_results = validate_and_clean_results(results_from_models)

    print(
        f"✅ Validated {len(validated_results)} out of {len(results_from_models)} results\n"
    )

    print("🎨 applying masks to files...")

    stats = apply_masks_to_files(validated_results, output_dir)

    print(f"\n{'=' * 60}")
    print("📊 masking statistics")
    print(f"{'=' * 60}")
    print(f"Total files processed: {stats['total']}")
    print(f"✅ successfully masked: {stats['success']}")
    print(f"❌ failed: {stats['failed']}")
    print(f"⚠️  skipped: {stats['skipped']}")
    print(f"{'=' * 60}")
    print(f"\n✅ masking completed! Files saved to: {output_dir}")


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print(f"🚀 starting process at {start_time}")

    asyncio.run(main())

    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    print(f"⏱️  execution finished. Total time: {total_time}")
