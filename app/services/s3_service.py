import os
import io
import uuid
import boto3
import pandas as pd
from dotenv import load_dotenv
from botocore.exceptions import BotoCoreError, ClientError
from app.core.logger import logger


class S3Service:
    """Service for handling S3 upload, download, and read operations."""

    def __init__(self):
        load_dotenv()  # Load environment variables

        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        if not all([self.bucket_name, aws_access_key, aws_secret_key]):
            logger.error("Missing AWS or S3 configuration in .env file.")
            raise ValueError("Missing AWS credentials or S3 bucket name in .env")

        # Initialize boto3 S3 client
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        logger.info(f"S3Service initialized for bucket: {self.bucket_name}")

    def upload_excel(self, file_path: str) -> str:
        """Upload an Excel file to S3 and return its unique file_id."""
        file_id = str(uuid.uuid4())
        s3_key = f"excels/{file_id}.xlsx"

        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            logger.info(f"Uploaded file → s3://{self.bucket_name}/{s3_key}")
            return file_id
        except (BotoCoreError, ClientError) as e:
            logger.exception(f"Failed to upload file {file_path}: {e}")
            raise

    def download_excel(self, file_id: str, download_dir: str = "downloads") -> str:
        """Download Excel file from S3 using its file_id."""
        s3_key = f"excels/{file_id}.xlsx"
        os.makedirs(download_dir, exist_ok=True)
        local_path = os.path.join(download_dir, f"{file_id}.xlsx")

        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"Downloaded s3://{self.bucket_name}/{s3_key} → {local_path}")
            return local_path
        except (BotoCoreError, ClientError) as e:
            logger.exception(f"Failed to download file {s3_key}: {e}")
            raise

    def fetch_excel_as_df(self, file_id: str) -> pd.DataFrame:
        """Fetch an Excel file from S3 and return it as a pandas DataFrame."""
        s3_key = f"excels/{file_id}.xlsx"

        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            data = response["Body"].read()
            df = pd.read_excel(io.BytesIO(data))
            logger.info(f"Fetched Excel as DataFrame from s3://{self.bucket_name}/{s3_key}")
            return df
        except (BotoCoreError, ClientError, Exception) as e:
            logger.exception(f"Failed to read Excel file from {s3_key}: {e}")
            raise
