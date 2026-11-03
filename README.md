# Gujarati Revenue AI — PS000216

Gujarati voice-first citizen assistant prototype for Gujarat Revenue Department services.

## Features in this starter
- Gujarati voice recording in browser
- Gujarati speech-to-text using faster-whisper
- RAG over uploaded official PDF documents
- LLM responses through a locally running Ollama model
- Gujarati speech output using gTTS
- React chat interface

## Requirements
- Python 3.10 or 3.11 recommended
- Node.js 20+
- FFmpeg installed and available on PATH
- Ollama installed with a multilingual model pulled

## 1. Start Ollama
```bash
ollama pull qwen2.5:7b
ollama serve
```
If your computer has limited RAM, use a smaller model and update `OLLAMA_MODEL` in `.env`.

## 2. Start backend
```bash
cd backend
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
The first run downloads Whisper and embedding models. This can take time and disk space.
API docs: http://localhost:8000/docs

## 3. Start frontend
Open another terminal:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## 4. Add verified revenue documents
Use Swagger UI at http://localhost:8000/docs:
- Find `POST /api/admin/knowledge/upload`
- Upload a text-based official PDF (not a scanned image PDF)
- Ask questions in the React app

Only ingest current, authentic documents from official government sources. Record each document's title, URL, publication/update date and retrieval date in your project documentation.

## Current limitations
- This is a student prototype, not an official government service.
- The PDF upload endpoint is unauthenticated. Do not expose it publicly; add admin authentication first.
- Application tracking and private land-record lookup are NOT connected. They require authorized government API access, identity verification and privacy/security review.
- gTTS sends text to an external service; do not send personal or confidential information to it.
- Whisper is configured for Gujarati (`gu`). Real-world accuracy must be tested across dialects, accents and noisy recordings.
- RAG similarity results are not automatically trustworthy. Validate retrieved sources and add a minimum relevance threshold before production.
- Scanned PDFs need OCR before indexing.
- Add rate limiting, file scanning, audit logs, HTTPS, consent, retention controls and role-based access before deployment.
