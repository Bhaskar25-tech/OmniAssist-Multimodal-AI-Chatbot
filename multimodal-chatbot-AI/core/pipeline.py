"""handle() sends a message (and optional image) to the right module."""
import os
import tempfile

from core.memory import ChatMemory
from core.router import route
from modules.module1_chat import reply
from modules.module2_code import generate_code
from modules.module3_summarize import read_url, summarize
from modules.module6_vision import explain_image
from modules.module8_documents import answer_question, load_document, summarize_document
from modules.module7_translate import parse_translate_request, translate, translate_image_text


def _image_suffix(data: bytes):
    if data[:2] == b"\xff\xd8":
        return ".jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return ".png"


def attach_document(memory: ChatMemory, data: bytes, filename: str) -> dict:
    """Reads an uploaded PDF/DOCX/TXT and stores it in the conversation memory."""
    suffix = os.path.splitext(filename)[1].lower() or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(data)
        path = f.name
    try:
        memory.document = load_document(path, name=filename)
    finally:
        os.remove(path)
    doc = memory.document
    return {"name": doc.name, "pages": doc.num_pages, "chunks": len(doc.chunks)}


SUMMARY_WORDS = ("summar", "tldr", "overview", "key points", "main points")


def handle(message: str, memory: ChatMemory, image_bytes: bytes = None) -> dict:
    """Returns {'task', 'answer', plus 'ocr_text' etc. for image tasks}."""
    message = message.strip()
    is_url = message.startswith(("http://", "https://"))
    task = route(message, has_image=image_bytes is not None,
                 has_long_text=len(message) > 1500 or is_url,
                 has_document=memory.document is not None)
    result = {"task": task}
    img_path = None

    try:
        if image_bytes is not None:
            with tempfile.NamedTemporaryFile(delete=False,
                                             suffix=_image_suffix(image_bytes)) as f:
                f.write(image_bytes)
                img_path = f.name

        if task == "image":
            answer, info = explain_image(img_path, message or "Explain this image.")
            result.update(info)
        elif task == "translate" and img_path:
            target, _ = parse_translate_request(message)
            answer, ocr_text = translate_image_text(img_path, target)
            result.update({"ocr_text": ocr_text, "target_language": target})
        elif task == "translate":
            target, text = parse_translate_request(message)
            answer = translate(text, target)
            result["target_language"] = target
        elif task == "document":
            if any(w in message.lower() for w in SUMMARY_WORDS):
                answer = summarize_document(memory.document)
            else:
                answer, pages = answer_question(memory.document, message, memory.get())
                result["pages_used"] = pages
            result["document"] = memory.document.name
        elif task == "code":
            answer = generate_code(message, history=memory.get())
        elif task == "summarize":
            answer = summarize(read_url(message) if is_url else message)
        else:
            answer = reply(memory.get(), message)
    finally:
        if img_path and os.path.exists(img_path):
            os.remove(img_path)

    memory.add("user", message or "[image]")
    memory.add("assistant", answer)
    result["answer"] = answer
    return result
