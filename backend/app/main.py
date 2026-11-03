import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.config import DOCUMENT_DIR
from app.services.speech_to_text import transcribe_audio
from app.services.text_to_speech import synthesize_gujarati
from app.services.document_processor import extract_text_from_pdf, chunk_text
from app.services.rag import KnowledgeBase
from app.services.llm import generate_answer

app = FastAPI(title="Gujarati Revenue AI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kb = KnowledgeBase()

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

@app.get("/health")
def health():
    return {"status": "ok", "service": "Gujarati Revenue AI"}

@app.post("/api/chat")
def chat(body: ChatRequest):
    try:
        sources = kb.search(body.message, top_k=4)
        answer = generate_answer(body.message, sources)
        return {
            "answer": answer,
            "sources": list(dict.fromkeys(x["source"] for x in sources)),
            "verified_context_found": bool(sources)
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {exc}")

@app.post("/api/voice/transcribe")
async def voice_transcribe(audio: UploadFile = File(...)):
    suffix = os.path.splitext(audio.filename or "recording.webm")[1] or ".webm"
    tmp_path = None
    try:
        content = await audio.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty audio file")
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        text = transcribe_audio(tmp_path)
        return {"text": text, "language": "gu"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/api/voice/speak")
def voice_speak(body: ChatRequest):
    try:
        audio = synthesize_gujarati(body.message)
        return StreamingResponse(audio, media_type="audio/mpeg",
                                 headers={"Content-Disposition": "inline; filename=response.mp3"})
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Gujarati TTS failed: {exc}")

@app.post("/api/admin/knowledge/upload")
async def upload_knowledge(file: UploadFile = File(...)):
    # Prototype endpoint only. Add admin authentication before any public deployment.
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Upload a PDF file")
    safe_name = os.path.basename(file.filename)
    path = os.path.join(DOCUMENT_DIR, safe_name)
    content = await file.read()
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF must be 15 MB or smaller")
    with open(path, "wb") as f:
        f.write(content)
    text = extract_text_from_pdf(path)
    chunks = chunk_text(text)
    count = kb.add_chunks(chunks, safe_name)
    return {"message": "Document indexed", "filename": safe_name, "chunks_added": count}
