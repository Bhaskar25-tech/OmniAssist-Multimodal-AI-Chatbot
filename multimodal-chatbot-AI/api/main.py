from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from core.memory import ChatMemory
from core.pipeline import attach_document, handle

app = FastAPI(title="Multimodal Chatbot API")
sessions = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/document")
async def upload_document(document: UploadFile = File(...), session_id: str = Form("default")):
    """Upload a PDF/DOCX/TXT. Later /chat messages in this session are answered from it."""
    memory = sessions.setdefault(session_id, ChatMemory())
    try:
        return attach_document(memory, await document.read(), document.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/chat")
async def chat(message: str = Form(""), session_id: str = Form("default"),
               image: Optional[UploadFile] = File(None)):
    memory = sessions.setdefault(session_id, ChatMemory())
    image_bytes = await image.read() if image else None
    return handle(message, memory, image_bytes)


@app.post("/reset")
def reset(session_id: str = Form("default")):
    sessions.pop(session_id, None)
    return {"status": "cleared"}
