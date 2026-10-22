"""Translation helpers for text and image OCR."""

import re

from core.config import ask
from modules.module5_ocr import extract_text

TARGET_LANGUAGES = {
    "english": "English",
    "hindi": "Hindi",
    "telugu": "Telugu",
    "tamil": "Tamil",
    "kannada": "Kannada",
    "malayalam": "Malayalam",
    "marathi": "Marathi",
    "bengali": "Bengali",
    "gujarati": "Gujarati",
    "urdu": "Urdu",
    "punjabi": "Punjabi",
    "french": "French",
    "spanish": "Spanish",
    "german": "German",
    "italian": "Italian",
    "japanese": "Japanese",
    "korean": "Korean",
    "chinese": "Chinese",
    "arabic": "Arabic",
    "russian": "Russian",
    "portuguese": "Portuguese",
}


def chunk_text(text, size=6000):
    if not text:
        return []
    return [text[i:i + size] for i in range(0, len(text), size)]


def parse_translate_request(message):
    text = message.strip()
    match = re.search(r"(?:translate|translat(e|ion))\s+(.*?)(?:\s+to\s+|$)", text, re.I)
    if match:
        target_part = text[match.end():].strip()
    else:
        target_part = ""
    target = ""
    lowered = text.lower()
    for lang, name in TARGET_LANGUAGES.items():
        if re.search(rf"\b{lang}\b", lowered):
            target = name
            break
    if not target:
        target = "English"
    if match:
        body = match.group(2).strip()
        if not body:
            body = target_part.replace("to " + target.lower(), "", 1).strip()
    else:
        body = text
    return target, body


def translate(text, target_language, source_language=None):
    if not text or not text.strip():
        return ""
    if not target_language or not target_language.strip():
        raise ValueError("Please specify a target language.")
    prompt = (
        f"Translate the following text from {source_language or 'the source language'} to {target_language}. "
        f"Keep the meaning and tone. Preserve line breaks. Reply with the translation only.\n\nTEXT:\n{text}"
    )
    return ask([{"role": "user", "content": prompt}], system="You are a professional translator.", max_tokens=1000)


def translate_image_text(image_path, target_language):
    text = extract_text(image_path)
    if not text.strip():
        return "No text found in the image.", ""
    return translate(text, target_language), text
