"""Simple chat module used by the app and evaluation scripts."""

from core.config import ask


def reply(history, message):
    """Return an answer using the configured model, with a safe offline fallback."""
    messages = list(history or [])
    messages.append({"role": "user", "content": message})
    return ask(messages, system="You are a helpful assistant. Be concise and factual.", max_tokens=600)
