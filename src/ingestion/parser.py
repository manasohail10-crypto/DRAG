from docling.datamodel.base_models import InputFormat, ConversionStatus
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from pathlib import Path
from tqdm import tqdm
from src.config.settings import setting
import logfire

def build_converter():
    logfire.info("Building Docling converter (OCR=False, table structure=True)")
    options = PdfPipelineOptions()
    options.do_ocr = False
    options.do_table_structure = True
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=options
            )
        }
    )
    logfire.info("Docling converter is ready")
    return converter
    
    
def parse_df(converter,pdf_path):
  pdf_path = Path(pdf_path)
  logfire.debug(f"Converting PDF: {pdf_path.name}")
  results = converter.convert(str(pdf_path))
  logfire.debug(f"Conversion status for {pdf_path.name}: {results.status}")
  if results.status != ConversionStatus.SUCCESS:
    logfire.error(f"Conversion failed: {pdf_path.name} | status: {results.status}")
    raise RuntimeError(f"PDF conversion failed: {pdf_path.name}")
  return results.document


def save_parsed_outputs(doc,record,parsed_dir):
  parsed_dir = Path(parsed_dir)
  base = f"{Path(record['file_name']).stem}__{record['doc_id']}"
  markdown_path = parsed_dir/f"{base}.md"
  markdown_text = doc.export_to_markdown()
  markdown_path.write_text(markdown_text,encoding='utf-8')
  logfire.info(f"Saved markdown: {markdown_path.name} | characters: {len(markdown_text)}")
  json_path = parsed_dir/f"{base}.json"
  doc.save_as_json(json_path)
  logfire.info(f"Saved json: {json_path.name}")
  return markdown_path

def parse_all_documents(records,parsed_dir=None):
  if parsed_dir is None:
    parsed_dir = setting.PARSED_DIR
  logfire.info(f"Start parsing {len(records)} PDF(s) into {parsed_dir}")
  converter = build_converter()
  parsed = []
  failed = []
  for record in tqdm(records,desc="Parsing PDFs"):
    with logfire.span("Parsing {file_name}", file_name=record['file_name']):  # span also shows time taken
      try:
        logfire.info(f"Parsing: {record['file_name']} | doc_id: {record['doc_id']}")
        docs = parse_df(converter,record['path'])
        save_parsed_outputs(docs,record,parsed_dir)
        parsed.append((record,docs))
        logfire.info(f"Parsed OK: {record['file_name']}")
      except Exception as e:
        logfire.exception(f"FAILED TO PARSE:{record['file_name']} | ERROR:{str(e)}")  # also saves the full traceback
        failed.append(record['file_name'])
  logfire.info(f"Parsing finished. Success: {len(parsed)}, Failed: {len(failed)}")
  if failed:
    logfire.warn(f"Failed files: {failed}")
  return parsed,failed