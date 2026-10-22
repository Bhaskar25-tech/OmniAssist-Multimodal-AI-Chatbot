"""Decides which module handles a message: chat / code / summarize / image / translate / document."""
import os
import re

from core.config import ask

LABELS = ["chat", "code", "summarize", "translate"]
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "router_model.joblib")
_clf = None
_clf_loaded = False

TRANSLATE_RE = re.compile(
    r"\btranslat\w*|\bhow (do|would) you say\b|\b(in|into|to) "
    r"(hindi|telugu|tamil|kannada|malayalam|marathi|bengali|gujarati|urdu|punjabi|"
    r"english|french|spanish|german|italian|japanese|korean|chinese|arabic|russian|portuguese)\b",
    re.I,
)

CODE_RE = re.compile(r"\b(write|generate|create|fix|debug)\b.*\b(code|python|function|program|script|class|sql)\b|```", re.I)
SUMMARY_RE = re.compile(r"\b(summari[sz]e|tl;?dr|key points)\b", re.I)


def _trained_model():
    global _clf, _clf_loaded
    if not _clf_loaded:
        _clf_loaded = True
        if os.path.exists(MODEL_PATH):
            import joblib
            _clf = joblib.load(MODEL_PATH)
    return _clf


def route(message, has_image=False, has_long_text=False, has_document=False):
    wants_translate = bool(TRANSLATE_RE.search(message))

    if has_image:
        return "translate" if wants_translate else "image"
    if has_document:                # a document is loaded: questions are about it
        return "document"
    if has_long_text and not wants_translate:
        return "summarize"
    if wants_translate:
        return "translate"

    clf = _trained_model()          # your own model from ml/train_router.py
    if clf is not None:
        return str(clf.predict([message])[0])

    if CODE_RE.search(message):      # cheap keyword check first
        return "code"
    if SUMMARY_RE.search(message):
        return "summarize"
    try:                             # fallback: LLM classifier
        out = ask(
            [{"role": "user", "content": f"Classify this message: {message}"}],
            system="Reply with exactly one word: chat, code, summarize or translate.",
            max_tokens=5,
        ).lower()
        out = re.sub(r"[^a-z]", "", out)
        return out if out in LABELS else "chat"
    except Exception:
        return "chat"
