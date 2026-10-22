"""Image understanding helper: vision model plus OCR text extraction."""
from modules.module5_ocr import extract_text
from core.config import ask_vision


def explain_image(path, question="Explain this image."):
    ocr_error = None
    try:
        ocr_text = extract_text(path)
    except Exception as exc:
        ocr_text, ocr_error = "", str(exc)

    prompt = question or "Describe this image."
    if ocr_text:
        prompt += "\nAlso consider this OCR text (which may contain mistakes):\n" + ocr_text
    answer = ask_vision(path, prompt, system="You are an accurate image understanding assistant. Describe only visible details and be explicit about uncertainty.", max_tokens=700)
    if ocr_error:
        answer += f"\n\n(OCR problem: {ocr_error})"
    return answer, {"ocr_text": ocr_text, "confidence": None, "engine": "tesseract/easyocr"}
