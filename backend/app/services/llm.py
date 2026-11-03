import requests
from app.config import OLLAMA_URL, OLLAMA_MODEL

SYSTEM_PROMPT = '''
You are a careful Gujarati-language assistant for citizens using Gujarat Revenue Department services.
Reply in clear, polite Gujarati unless the citizen asks for another language.
Use ONLY the supplied official context for government rules, document lists, fees, deadlines and procedures.
If the context does not contain the answer, say that you cannot verify it and direct the citizen to the relevant official portal or office.
Never invent application status, land ownership, survey numbers, fees, legal advice, or government rules.
For private application or land-record data, explain that authenticated authorized access is required.
Keep answers concise and practical. Distinguish general guidance from confirmed official information.
'''

def generate_answer(question: str, context_items: list) -> str:
    context = "\n\n".join(
        f"Source: {x['source']}\nContent: {x['text']}" for x in context_items
    ) or "No verified document context was found."
    prompt = f"{SYSTEM_PROMPT}\n\nVERIFIED CONTEXT:\n{context}\n\nCITIZEN QUESTION:\n{question}\n\nAnswer:"
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()
