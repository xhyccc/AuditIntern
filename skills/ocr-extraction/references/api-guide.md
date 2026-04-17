# OCR Extraction — API Reference

## Function Signature

```python
from skills.ocr_extraction.scripts.skill_ocr_extraction import run

result = run(
    file_path="uploads/invoice_scan.png",
    output_path="results/ocr_result.json"
)
```

## OpenCode CLI — Intent Name

`run_ocr`

## Required Parameters

| Parameter   | Type   | Description                                          |
|-------------|--------|------------------------------------------------------|
| `file_path` | string | Path to image (PNG/JPG/JPEG/TIFF/BMP) or PDF file   |

## Optional Parameters

| Parameter     | Type   | Default           | Description           |
|---------------|--------|-------------------|-----------------------|
| `output_path` | string | `ocr_result.json` | JSON output file path |

## Supported File Types

| Extension                               | Backend                   | Requirements              |
|-----------------------------------------|---------------------------|---------------------------|
| `.png`, `.jpg`, `.jpeg`, `.tiff`, `.tif`, `.bmp` | Tesseract via pytesseract | `pytesseract`, `Pillow`  |
| `.pdf`                                  | pdfplumber                | `pdfplumber`              |

## Confidence Score

- **Images**: average of per-word confidence values (0–100) reported by Tesseract, divided by 100. Words with confidence < 0 are excluded.
- **PDFs**: fixed value of `0.95` for text-layer PDFs.

## Tesseract Language Configuration

Default Tesseract language is determined by the system installation. To specify a language:

```python
# Modify _extract_image() in the script:
text = pytesseract.image_to_string(img, lang="chi_sim+eng")
```

## Dependencies

| Package        | Purpose                     |
|----------------|-----------------------------|
| `pytesseract`  | Image OCR (wraps Tesseract) |
| `Pillow`       | Image loading               |
| `pdfplumber`   | PDF text extraction         |

## System Requirements

- Tesseract OCR must be installed: `apt-get install tesseract-ocr`
- For Chinese: `apt-get install tesseract-ocr-chi-sim`
