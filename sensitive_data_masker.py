import asyncio
import datetime
import os

from src.modules.sensitive_data_masker.gemini import (
    process_files_with_coordinate_matching,
)
from src.modules.sensitive_data_masker.args import get_args


async def main():
    args = get_args()
    real_path = os.path.realpath(args.input)
    output_dir = os.path.abspath(args.output)

    print("🎯 Starting sensitive data masking with coordinate templates...")

    stats = await process_files_with_coordinate_matching(real_path, output_dir)

    print(f"\n{'=' * 60}")
    print("📊 MASKING SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total files processed: {stats['total']}")
    print(f"✅ Successfully masked: {stats['success']}")
    print(f"⚠️  No matching template: {stats['no_match']}")
    print(f"❌ Errors: {stats['error']}")
    print(f"{'=' * 60}")

    if stats["success"] > 0:
        print(f"\n✅ Masking completed! Files saved to: {output_dir}")
    elif stats["no_match"] > 0:
        print(
            "\n⚠️  No matches found. Consider creating templates for these file formats."
        )
    else:
        print("\n❌ Processing failed. Check the errors above.")


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print(f"🚀 starting process at {start_time}")

    asyncio.run(main())

    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    print(f"⏱️  execution finished. Total time: {total_time}")
