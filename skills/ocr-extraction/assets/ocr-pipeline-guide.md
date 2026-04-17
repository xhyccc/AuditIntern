# OCR Pipeline Guide

This guide describes common workflows for using the `ocr-extraction` skill as the first stage in a multi-step audit pipeline.

## Pipeline 1: Scanned Invoice → Field Extraction

```
[Scanned Invoice PNG]
       ↓  run_ocr
[Extracted Text JSON]
       ↓  run_contract_parse
[Structured Fields: amount, date, parties]
```

## Pipeline 2: PDF Bank Statement → Fraud Scan

```
[PDF Bank Statement]
       ↓  run_ocr
[Extracted Text]
       ↓  (save as CSV manually or with script)
[Journal Entry CSV]
       ↓  run_fraud_scan
[Risk Flags + Benford Result]
```

## Pipeline 3: Scanned Contract → Legal Search

```
[Scanned Contract TIFF]
       ↓  run_ocr
[Contract Text]
       ↓  run_rag_search (query from extracted terms)
[Relevant Regulatory Passages]
```

## Pre-processing Tips

| Issue                  | Solution                                          |
|------------------------|---------------------------------------------------|
| Low confidence (<0.70) | Increase image resolution (300 DPI minimum)       |
| Skewed scan            | Deskew image before passing to OCR                |
| Scanned PDF            | Convert PDF pages to PNG first (e.g. with `pdf2image`) |
| Mixed Chinese/English  | Install `chi_sim` and `eng` Tesseract language packs |
| Tables in PDF          | Use pdfplumber's `extract_table()` directly for better results |

## Minimum Image Quality Requirements

- Resolution: ≥ 300 DPI
- Format: PNG preferred over JPEG (avoids compression artifacts)
- Background: white or near-white
- Font size: ≥ 10pt
