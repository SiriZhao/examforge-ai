# OCR Providers

Supported providers:

- `local_tesseract`: uses local Tesseract.
- `custom_api`: sends image data to a caller-provided endpoint.
- `openai_vision`: placeholder for OpenAI vision-compatible OCR.

For scanned PDFs, each page is text-extracted first. If a page has fewer than 20 characters, it is rendered to an image and OCR is used as fallback.

Local OCR requires Tesseract and, for PDF rendering, Poppler.

## Add a Provider

Add a new provider under `backend/app/services/ocr_providers/`, subclass `BaseOCRProvider`, then register it in `registry.py`. Provider implementations must only receive API keys through request config or environment variables and must never log them.
