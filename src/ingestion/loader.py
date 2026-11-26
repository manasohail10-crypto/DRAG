from pathlib import Path
import hashlib
import logfire
from src.config.settings import setting
from src.aws.s3_store import download_folder_from_s3


def find_pdf_files(folder):
  folder = Path(folder)
  if not folder.exists():
    return []
  pdf_files = [file for file in folder.rglob("*") 
  if file.is_file() and file.suffix.lower() == ".pdf"]  # FIX 1: "or" -> "and", FIX 2: suffix() -> suffix
  return sorted(pdf_files)


def compute_doc_id(pdf_path):
  pdf_path = Path(pdf_path)
  hasher = hashlib.sha256()
  with open(pdf_path,'rb') as file:
    while True:
      piece = file.read(1024*1024)
      if not piece:
        break
      hasher.update(piece)
  return hasher.hexdigest()[:12]


def load_documents(folder=None):
  if folder is None:
    folder = setting.RAW_DIR
  folder = Path(folder)
  pdf_files = find_pdf_files(folder)
  records = []
  seen_id = set()
  for path in pdf_files:
    doc_ids = compute_doc_id(path)
    if doc_ids in seen_id:
      logfire.warn(f"Duplicate file, skipped: {path}")  # FIX 3: logfire does not use %s style
      continue
    seen_id.add(doc_ids)
    records.append({
      "doc_id": doc_ids,
      "file_name": path.name,
      "path": path
    })
  if not records:
    logfire.warn(f"No PDFs found in {folder}")  # FIX 3
  return records

def sync_raw_from_s3():
  raw_dir = setting.RAW_DIR
  raw_pfx = setting.S3_RAW_PREFIX
  downloaded = download_folder_from_s3(raw_pfx, raw_dir)  # FIX 4: arguments were in the wrong order
  logfire.info(f"FILES:{downloaded}")
  return downloaded