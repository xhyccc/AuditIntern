"""
Skill: OCR Extraction
Extracts text and structured fields from images or PDF files.
"""

import json
import pathlib


def run(file_path: str, output_path: str) -> dict:
    path = pathlib.Path(file_path)
    suffix = path.suffix.lower()
    text = ""
    page_count = 0
    confidence = 0.0

    try:
        if suffix in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}:
            text, confidence, page_count = _extract_image(str(path))
        elif suffix == ".pdf":
            text, confidence, page_count = _extract_pdf(str(path))
        else:
            result = {
                "status": "error",
                "text": "",
                "confidence": 0.0,
                "page_count": 0,
                "message": f"Unsupported file type: {suffix}",
            }
            _write(output_path, result)
            return result
    except Exception as exc:
        result = {
            "status": "error",
            "text": str(text),
            "confidence": 0.0,
            "page_count": page_count,
            "message": str(exc),
        }
        _write(output_path, result)
        return result

    result = {
        "status": "ok",
        "text": text,
        "confidence": round(confidence, 4),
        "page_count": page_count,
    }
    _write(output_path, result)
    return result


def _extract_image(file_path: str):
    import pytesseract
    from PIL import Image

    img = Image.open(file_path)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    text = pytesseract.image_to_string(img)
    confs = [int(c) for c in data["conf"] if str(c).lstrip("-").isdigit() and int(c) >= 0]
    avg_conf = sum(confs) / len(confs) / 100.0 if confs else 0.0
    return text, avg_conf, 1


def _extract_pdf(file_path: str):
    import pdfplumber

    pages_text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            pages_text.append(page.extract_text() or "")
    text = "\n".join(pages_text)
    return text, 0.95, len(pages_text)


def _write(output_path: str, data: dict) -> None:
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
