"""Text summarization helpers."""

from bs4 import BeautifulSoup
import requests

from core.config import ask


def chunk_text(text, size=6000):
    if not text:
        return []
    return [text[i:i + size] for i in range(0, len(text), size)]


def summarize(text, style="concise bullet points"):
    if not text or not text.strip():
        return "No text available to summarize."
    chunks = chunk_text(text)
    partials = []
    for chunk in chunks:
        prompt = f"Summarize this source section faithfully. Do not invent facts.\n\n{chunk}"
        partials.append(ask([{"role": "user", "content": prompt}], system="You are a careful summarizer.", max_tokens=500))
    combined = partials[0] if len(partials) == 1 else "\n\n".join(partials)
    return ask([
        {"role": "user", "content": f"Create one {style} summary from the source material below. Preserve important facts and avoid repetition.\n\n{combined}"}
    ], system="You are a careful summarizer.", max_tokens=700)


def read_url(url):
    response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)
