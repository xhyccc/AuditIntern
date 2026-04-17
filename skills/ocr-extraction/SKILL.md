---
name: ocr-extraction
description: Extracts text and structured fields from images or PDF files using OCR. Use when the user asks to extract text from a scanned document, read a PDF, process an image file (PNG, JPG, TIFF), perform OCR, or digitize a paper-based financial document.
---

# OCR Extraction

Accepts an image (PNG/JPG/TIFF/BMP) or PDF file path. Uses Tesseract for images and
pdfplumber for PDFs to extract full text and compute a confidence score.

## Script

`scripts/skill_ocr_extraction.py` — `run(file_path, output_path) -> dict`
