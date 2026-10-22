"""OCR helpers for document and image text extraction."""

import shutil
from pathlib import Path


PREFERRED_LANGS = ["eng", "hin", "tel"]
WINDOWS_PATH = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")


def _setup_tesseract():
    import pytesseract
    """Find the Tesseract program on Windows/Mac/Linux, or explain how to install it."""
    if shutil.which("tesseract"):
        return
    if WINDOWS_PATH.exists():
        pytesseract.pytesseract.tesseract_cmd = str(WINDOWS_PATH)
        return
    raise RuntimeError(
        "Tesseract OCR program is not installed. Windows: install from "
        "https://github.com/UB-Mannheim/tesseract/wiki (default folder), then restart. "
        "Linux: sudo apt install tesseract-ocr. Mac: brew install tesseract."
    )


def _languages():
    import pytesseract
    """Use only the language packs that are actually installed (eng always works)."""
    installed = set(pytesseract.get_languages(config=""))
    langs = [l for l in PREFERRED_LANGS if l in installed]
    return "+".join(langs) if langs else "eng"


def extract_text(image_path):
    import cv2
    import pytesseract
    from modules.module4_opencv import preprocess
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Could not read the image: {path}")

    try:
        _setup_tesseract()
    except RuntimeError:
        # EasyOCR is a fallback; its first run may download model weights.
        try:
            import easyocr
            reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            results = reader.readtext(str(path), detail=0, paragraph=True)
            return "\n".join(str(item).strip() for item in results if str(item).strip())
        except Exception as exc:
            raise RuntimeError("Neither Tesseract nor EasyOCR could run OCR. Install Tesseract or check EasyOCR. " + str(exc)) from exc

    import pytesseract
    lang = _languages()
    # Try the cleaned-up image first, then the plain grayscale one; keep the longer result.
    candidates = []
    for img in (preprocess(image), cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)):
        candidates.append(pytesseract.image_to_string(img, lang=lang, config="--oem 3 --psm 6").strip())
    return max(candidates, key=len)
