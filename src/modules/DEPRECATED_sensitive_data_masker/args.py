import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description="llm-liaa-payment-receipt-sensitive-data-masker"
    )
    parser.add_argument(
        "-p",
        "--path",
        required=True,
        help="path to the payments receipts to mask sensitive data",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default="classify_output",
        help="output path",
    )
    args = parser.parse_args()
    return args
