"""Local OCR using EasyOCR. Supports paths, bytes, PIL images and Streamlit uploads."""

from functools import lru_cache
from io import BytesIO
from pathlib import Path

import easyocr
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


@lru_cache(maxsize=1)
def get_reader():
    """Load the English OCR model once and reuse it."""
    return easyocr.Reader(["en"], gpu=False, verbose=False)


def load_image(image_input):
    """Convert supported image input into an RGB PIL image."""
    if isinstance(image_input, Image.Image):
        image = image_input.copy()
    elif isinstance(image_input, (str, Path)):
        with Image.open(image_input) as source:
            image = source.copy()
    elif isinstance(image_input, bytes):
        with Image.open(BytesIO(image_input)) as source:
            image = source.copy()
    elif hasattr(image_input, "getvalue"):
        with Image.open(BytesIO(image_input.getvalue())) as source:
            image = source.copy()
    elif hasattr(image_input, "read"):
        with Image.open(BytesIO(image_input.read())) as source:
            image = source.copy()
    else:
        raise ValueError("Unsupported image input. Use a path, bytes, PIL image, or Streamlit upload.")

    return ImageOps.exif_transpose(image).convert("RGB")


def extract_text_from_image(image_input):
    """Extract English text from an image and return it as a string."""
    try:
        image = load_image(image_input)
        results = get_reader().readtext(np.asarray(image), detail=0, paragraph=True)
        return "\n".join(
            text.strip() for text in results
            if isinstance(text, str) and text.strip()
        )
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError(f"Unable to open image: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"OCR extraction failed: {exc}") from exc
