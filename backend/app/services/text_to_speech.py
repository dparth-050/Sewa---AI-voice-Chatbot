from gtts import gTTS
from io import BytesIO

def synthesize_gujarati(text: str) -> BytesIO:
    audio = BytesIO()
    gTTS(text=text, lang="gu", slow=False).write_to_fp(audio)
    audio.seek(0)
    return audio
