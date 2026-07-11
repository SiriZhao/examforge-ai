# OCR Providers

CampusForge extracts embedded text first and only uses OCR when a page or image needs it. This avoids wasting time on text PDFs and improves cloud performance.

## Current Strategy

- PDF pages with enough text are parsed directly.
- Scanned or low-text pages are sent through OCR.
- Images are OCR candidates.
- DOCX, PPTX, Markdown, and TXT are parsed without OCR.
- OCR results can be cached by file hash.

## Local Providers

Preferred local OCR path:

- RapidOCR when available.

Fallback path:

- Tesseract when enabled and installed.

Windows subprocess calls should hide console windows to avoid flashing terminals during OCR.

## Cloud Deployments

Cloud deployments should install OCR dependencies inside the Docker image and should not depend on the user's machine. Configure provider behavior with:

- `ENABLE_LOCAL_OCR`
- `ENABLE_RAPIDOCR`
- `ENABLE_TESSERACT`
- `OCR_CACHE_DIR`

## Provider Guidelines

When adding an OCR provider:

1. Add it under `backend/app/services/ocr_providers/`.
2. Register it in the provider registry.
3. Never log user API keys or full document contents.
4. Continue processing when only some pages fail.
5. Add tests for cache use, text-layer skipping, and failure fallback.
