---
name: ocr-extraction
description: Extracts text and structured fields from images or PDF files using OCR. Use when the user asks to extract text from a scanned document, digitize a paper invoice or receipt, read a PDF file, process an image (PNG, JPG, TIFF), perform optical character recognition, or convert a physical document into machine-readable text for further audit processing.
---

# OCR Extraction

## Overview

The **OCR extraction** skill converts scanned documents and PDF files into machine-readable text. It supports two extraction backends:

- **Images** (PNG, JPG, JPEG, TIFF, TIF, BMP): uses [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) via `pytesseract` and PIL. Returns the full extracted text plus a confidence score averaged across all recognized words.
- **PDFs**: uses [pdfplumber](https://github.com/jsvine/pdfplumber) to extract embedded text from each page. Returns concatenated text and a fixed confidence of 0.95 (text-layer PDFs). For scanned PDFs (no text layer), the text may be empty — use an image-based workflow instead.

The extracted text can then be passed to `llm-contract-parser`, `rag-legal-search`, or other downstream skills.

---

## OpenCode CLI Invocation

### Image file

```bash
echo '{
  "intent": "run_ocr",
  "params": {
    "file_path": "uploads/invoice_scan.png",
    "output_path": "results/ocr_result.json"
  }
}' | python -m src.cli.main
```

### PDF file

```bash
echo '{
  "intent": "run_ocr",
  "params": {
    "file_path": "uploads/contract.pdf",
    "output_path": "results/ocr_result.json"
  }
}' | python -m src.cli.main
```

### Via instruction file

`ocr_instruction.json`:
```json
{
  "intent": "run_ocr",
  "params": {
    "file_path": "uploads/bank_statement.pdf",
    "output_path": "results/ocr_result.json"
  }
}
```

```bash
python -m src.cli.main --instruction ocr_instruction.json
```

### Via REST API

```bash
# First upload the file:
curl -X POST http://localhost:8000/upload/{project_id} \
  -F "file=@invoice_scan.png"

# Then run OCR using the returned path:
curl -X POST http://localhost:8000/sessions/{session_id}/tasks \
  -H "Content-Type: application/json" \
  -d '{"intent": "run_ocr", "params": {"file_path": "uploads/invoice_scan.png"}}'
```

---

## Parameters

| Parameter     | Type   | Required | Default             | Description                                                     |
|---------------|--------|----------|---------------------|-----------------------------------------------------------------|
| `file_path`   | string | ✅ Yes   | —                   | Path to image (PNG/JPG/JPEG/TIFF/BMP) or PDF file              |
| `output_path` | string | No       | `ocr_result.json`   | Path to write the JSON result report                            |

---

## Supported File Types

| Extension            | Backend        | Notes                                          |
|----------------------|----------------|------------------------------------------------|
| `.png`, `.jpg`, `.jpeg`, `.tiff`, `.tif`, `.bmp` | Tesseract / PIL | Requires `pytesseract` and `Pillow`  |
| `.pdf`               | pdfplumber     | Extracts embedded text; scanned PDFs may be empty |
| Other                | —              | Returns `status: error`                        |

---

## Output Schema

```json
{
  "status": "ok",
  "text": "INVOICE\nDate: 2024-03-15\nAmount: ¥45,000\nVendor: ABC Supplies Co.\n...",
  "confidence": 0.8743,
  "page_count": 1
}
```

| Field        | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| `status`     | `"ok"` on success, `"error"` on unsupported type or extraction failure     |
| `text`       | Full extracted text (newline-separated lines)                               |
| `confidence` | Average word-level confidence [0.0–1.0]; 0.95 for text-layer PDFs         |
| `page_count` | Number of pages processed                                                   |

---

## Chaining with Other Skills

After extraction, pipe the `text` field to other skills:

```bash
# Step 1: OCR
echo '{"intent":"run_ocr","params":{"file_path":"contract.pdf","output_path":"ocr.json"}}' \
  | python -m src.cli.main

# Step 2: Parse contract fields from extracted text
cat ocr.json | python -c "
import json, sys
ocr = json.load(sys.stdin)
instruction = {
  'intent': 'run_contract_parse',
  'params': {'text': ocr['text'], 'output_path': 'contract_fields.json'}
}
print(json.dumps(instruction))
" | python -m src.cli.main
```

---

## Notes & Edge Cases

- **Tesseract language**: by default uses the installed Tesseract language pack. For Chinese documents, install `tesseract-lang` with `chi_sim` or `chi_tra`.
- **Scanned PDFs**: pdfplumber only extracts embedded text. Scanned PDFs will return empty `text`. Use the image extraction path instead by converting PDF pages to images first.
- **Confidence**: image confidence is averaged across all words with confidence ≥ 0. Blank pages or unrecognizable images return 0.0.

---

## Script

`scripts/skill_ocr_extraction.py` — `run(file_path: str, output_path: str) -> dict`
