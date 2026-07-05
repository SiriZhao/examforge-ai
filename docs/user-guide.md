# ExamForge AI User Guide

## Web App

1. Open the deployed ExamForge AI URL.
2. Enter a course or exam name.
3. Upload courseware, textbooks, notes, past exams, scanned PDFs, images, Markdown, TXT, DOCX, or PPTX files.
4. Choose study goal, exam type, OCR mode, detail level, and output style.
5. Enable AI deep organization when you have a DeepSeek or OpenAI-compatible API key, or use local safe draft mode without a key.
6. Click Generate and wait for parsing, OCR, evidence building, chunked LLM processing, quality checks, and export preparation.
7. Review study units, high-frequency topics, question type analysis, mock exam, Anki cards, sprint plan, quality score, and generation summary.
8. Download Markdown, Word, PDF, or Anki CSV.

## Long Materials

For large PDFs or many files, ExamForge AI automatically switches to chunked LLM processing. It extracts chunk insights first, then synthesizes a final report. If the model still reports `CONTEXT_TOO_LONG`, the system retries with a compact evidence pack before falling back to the local safe draft.

## API Key Options

- Server key: the deployment owner configures a key in environment variables. Users can use AI mode directly.
- User key: the user enters a key in the browser. The server uses it for the request and should not persist it.
- No key: the app generates a local safe draft.

Use HTTPS when sending a user-provided API key.
