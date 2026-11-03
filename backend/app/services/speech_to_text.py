from faster_whisper import WhisperModel
from app.config import WHISPER_MODEL

# First run downloads the selected model. CPU/int8 is a practical laptop default.
_model = None

def transcribe_audio(path: str) -> str:
    global _model
    if _model is None:
        _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, info = _model.transcribe(path, language="gu", beam_size=5, vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments).strip()
