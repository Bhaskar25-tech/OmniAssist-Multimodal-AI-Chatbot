# Multimodal AI Chatbot

One chatbot that can: chat, generate code (with test run + self-fix), summarize text/PDF/URLs, read uploaded documents (PDF/DOCX/TXT) and answer questions from them with page citations,
translate between human languages, and read + explain images (OpenCV + OCR + vision model).

## Architecture
```
User (text and/or image) -> ui/app.py -> api/main.py -> core/pipeline.py -> core/router.py
   chat -> module1 | code -> module2 | summarize -> module3
   document -> module8 (extract -> chunk -> retrieve -> answer with page numbers)
   translate -> module7 | image -> module4 (OpenCV) -> module5 (OCR) -> module6 (vision)
```

## Setup
1. Install Python 3.10+ and the Tesseract OCR program
   (Windows: UB Mannheim installer, Ubuntu: `sudo apt install tesseract-ocr`).
2. `python -m venv .venv` and activate it, then `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`. Default setup uses Ollama locally and does not require an API key. Install Ollama and run `ollama pull llama3.2` and `ollama pull qwen2.5vl:3b`.
4. Optional: `python -m ml.train_router` to train your own router.

## Run (always from the project root)
- UI: `streamlit run ui/app.py`
- API: `uvicorn api.main:app --reload`  (POST `/chat`: form fields `message`, optional `image`)
- Docker: `docker compose up --build`
- Test a single module: `python -m modules.module1_chat` (same for module2 ... module7)
- Unit tests (offline): `python -m pytest tests`

## Evaluation
See `evaluation/results.md`. Scripts: `eval_chat`, `test_code_tasks`, `eval_ocr`.

## Document reader
Upload a PDF, DOCX or TXT in the UI sidebar (or POST it to `/document`). Then ask questions or say
"summarize". Answers cite page numbers. Scanned PDF pages are read with OCR automatically.
Retrieval uses TF-IDF (no extra downloads). For better meaning-based search, swap in
sentence-transformers embeddings + FAISS/Chroma inside `DocumentStore`.

## Notes
- Code execution uses a subprocess with a timeout. It is not a secure sandbox; use Docker for public use.
- OCR for Hindi/Telugu needs the language packs; edit `TESSERACT_LANGS` / `EASYOCR_LANGS` in `module5_ocr.py`.
- OCR can make mistakes, so the UI shows the extracted text for verification.


## Local Ollama setup (Windows PowerShell)
```powershell
 copy .env.example .env
 python -m venv .venv
 .\.venv\Scripts\Activate.ps1
 python -m pip install --upgrade pip
 pip install -r requirements.txt
 ollama pull llama3.2
 ollama pull qwen2.5vl:3b
 streamlit run ui/app.py
```
The Streamlit UI calls the shared pipeline directly; a separate API server is optional. Run `python check_setup.py` for diagnostics. OCR uses Tesseract if installed and falls back to EasyOCR if it is not.
