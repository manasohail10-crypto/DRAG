import logfire
from pathlib import Path
from src.config.settings import setting
import argparse
from src.aws.clients import get_s3_client  
from src.aws.s3_store import create_bucket_if_missing, upload_folder_to_s3  
from dotenv import load_dotenv

load_dotenv()
logfire.configure()


def ensure_data_folders():
    folders = [
        Path(setting.RAW_DIR),
        Path(setting.PARSED_DIR),
        Path(setting.PROCESSED_DIR),
    ]
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
  
def parse_args():
    parser = argparse.ArgumentParser(description="Create the S3 bucket and upload raw PDFs.")
    parser.add_argument(
        "--upload-raw",
        action="store_true",
        help="Also upload the PDFs from the raw data folder to S3.",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    bucket = setting.S3_BUCKET_NAME
    ensure_data_folders()
    create_bucket_if_missing()

    if args.upload_raw:
        count = upload_folder_to_s3(setting.RAW_DIR, setting.S3_RAW_PREFIX)
        print(f"Uploaded {count} PDF(s).")

    print(f"Bucket address: s3://{bucket}/{setting.S3_RAW_PREFIX}")


if __name__ == "__main__":
    main()


