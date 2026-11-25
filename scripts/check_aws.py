import logfire
from src.aws.clients import get_boto3_session,get_s3_client
from src.config.settings import setting
from botocore.exceptions import ClientError
from src.aws.s3_store import list_s3_objects
from dotenv import load_dotenv

load_dotenv()
logfire.configure()


def check_identity():
  sts = get_boto3_session().client("sts")  # FIX 1: cleint -> client
  identity = sts.get_caller_identity()
  logfire.debug(f"ACCOUNT:{identity['Account']}")
  logfire.debug(f"ARN:{identity['Arn']}")
  return identity

def check_bucket_access():
  bucket_name = setting.S3_BUCKET_NAME
  client = get_s3_client()
  try:
    client.head_bucket(Bucket=bucket_name)
    logfire.info(f"BUCKET IS ALREADY EXIST:{bucket_name}")
    # FIX 2: removed "return False" here, it stopped the code below from running
  except ClientError as error:
    code = error.response['Error']['Code']
    if code in ("404","NoSuchBucket"):  # FIX 3: == tuple -> in tuple
      logfire.error("Bucket not created yet. Run: python -m scripts.setup_s3")
      return False
    if code == "403":
      logfire.error("No access. Check the bucket name and your IAM policy")
      return False
    raise
  objects = list_s3_objects("")  # FIX 4: object -> objects (name did not match the lines below)
  logfire.debug(f"Bucket '{bucket_name}' is OK. Files found: {len(objects)}")  # FIX 5: bucket -> bucket_name
  for key,size in objects[:5]:
    print(f"{key}")
  return True

def main():
  logfire.info(f"REGION-SETTING:{setting.AWS_REGION}")
  check_identity()
  check_bucket_access()

if __name__ == "__main__":
  main()