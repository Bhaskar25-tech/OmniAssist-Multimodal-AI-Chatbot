import cv2
import numpy as np

from evaluation.eval_ocr import cer, wer
from modules.module4_opencv import preprocess


def test_cer_wer():
    assert cer("hello", "hello") == 0
    assert round(cer("abcd", "abcf"), 2) == 0.25
    assert wer("a b c d", "a b x d") == 0.25


def test_preprocess_returns_binary_image():
    img = np.full((200, 400, 3), 255, np.uint8)
    cv2.putText(img, "Hello OCR", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4)
    out = preprocess(img)
    assert out.ndim == 2 and set(np.unique(out)).issubset({0, 255})
