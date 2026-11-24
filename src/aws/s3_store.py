from src.config.settings import setting
from dotenv import load_dotenv
from src.aws.clients import get_s3_client
from botocore.exceptions import ClientError
from pathlib import Path
import logfire

# FIX 2: removed the random "buckets" import (auto-import by mistake)

load_dotenv()
logfire.configure()

DEFAULT_REGION = "us-east-1"  # FIX 3: S3 needs no LocationConstraint only in us-east-1

def create_bucket_if_missing(bucket_name=None):
  if bucket_name is None:
    bucket_name = setting.S3_BUCKET_NAME
  client = get_s3_client()
  region = setting.AWS_REGION
  try:
    client.head_bucket(Bucket=bucket_name)
    logfire.info(f"BUCKET ALREADY EXIST: {bucket_name}")  # FIX 4: logfire does not take extra positional args
    return False
  except ClientError as error:
    code = error.response['Error']['Code']
    if code == "403":
      raise PermissionError(
        f"Bucket name '{bucket_name}' is taken by another AWS account. "
        "Choose a Different Bucket Name"
      ) from error
    if code not in ("404","NoSuchBucket"):
      raise
  
  create_arg = {"Bucket":bucket_name}
  if region != DEFAULT_REGION:
    create_arg['CreateBucketConfiguration'] = {'LocationConstraint':region}
  client.create_bucket(**create_arg)
  logfire.info(f"BUCKET:{bucket_name} CREATED IN {region}")
  return True  # FIX 5: return True when bucket is created

def upload_file_to_s3(local_path,key,bucket_name=None):
  if bucket_name is None:
    bucket_name = setting.S3_BUCKET_NAME
  client = get_s3_client()
  client.upload_file(str(local_path),bucket_name,key)
  s3_path = f"s3://{bucket_name}/{key}"
  logfire.info(f"FILE UPLOADED TO S3 {s3_path}")  # FIX 6: infO -> info
  return s3_path

def upload_folder_to_s3(local_dir,prefix,extenstion=(".pdf",)):
  count = 0
  local_dir = Path(local_dir)
  for path in local_dir.rglob("*"):
    if not path.is_file():  # FIX 7: missing ()
      continue
    if path.suffix.lower() not in extenstion:  # FIX 8: missing ()
      continue
    key = prefix + path.relative_to(local_dir).as_posix()  # FIX 9: missing ()
    upload_file_to_s3(path, key)  # FIX 10: was calling itself, should call the file upload
    count +=1
  logfire.info(f"Uploaded {count} file(s) from {local_dir}")  # FIX 11: logfire has no %d style
  return count

def list_s3_objects(prefix):
  bucket = setting.S3_BUCKET_NAME
  client = get_s3_client()
  paginator = client.get_paginator("list_objects_v2")
  object = []
  for page in paginator.paginate(Bucket=bucket,Prefix=prefix):
    for item in page.get("Contents",[]):
      if item['Key'].endswith('/'):
        continue
      object.append((item['Key'],item['Size']))
  return object

def download_folder_to_s3(prefix,local_dir):
  downloaded = 0
  skipped = 0
  bucket = setting.S3_BUCKET_NAME
  local_dir = Path(local_dir)
  client = get_s3_client()
  for key,size in list_s3_objects(prefix):  # FIX 12: function was not called
    local_path = local_dir/key[len(prefix):]
    local_path.parent.mkdir(parents=True,exist_ok=True)
    if local_path.exists() and local_path.stat().st_size == size:  # FIX 13: exist -> exists
      skipped +=1
      continue
    client.download_file(bucket,key,str(local_path))
    downloaded +=1
  logfire.info(f"Downloaded {downloaded} file(s), skipped {skipped}, into {local_dir}")  # FIX 14