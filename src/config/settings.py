from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)

class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")
    AWS_REGION: str
    S3_BUCKET_NAME: str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    PORTKEY_API_KEY: str
    LANGSMITH_TRACING: bool
    LANGSMITH_ENDPOINT: str
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str

    RAW_DIR: str = "data/raw"
    PARSED_DIR: str= "data/parsed"
    PROCESSED_DIR: str = "data/processed"
    S3_RAW_PREFIX: str = "raw/"

setting = Setting()