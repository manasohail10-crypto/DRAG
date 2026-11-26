import boto3
import logfire
from src.config.settings import setting
from botocore.config import Config
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()
logfire.configure()

@lru_cache(maxsize=1)
def get_boto3_session():
  logfire.info("CREATING A NEW BOTO SESSION")
  return boto3.Session(region_name=setting.AWS_REGION)

@lru_cache(maxsize=1)
def get_s3_client():
  logfire.info("Creating a NEW S3 CLIENT")
  that_config = Config(retries={"max_attempts":5,"mode":'standard'})
  client = get_boto3_session().client("s3",config=that_config)
  return client  