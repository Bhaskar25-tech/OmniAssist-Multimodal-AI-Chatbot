"""Document ingestion and retrieval helpers."""

import os

from core.config import ask


class DocumentStore:
    def __init__(self, name, text, pages):
        self.name = name
        self.text = text
        self.pages = pages
        self.num_pages = len(pages)
        self.chunks = pages


def _read_text_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def load_document(path, name=None):
    name = name or os.path.basename(path)
    suffix = os.path.splitext(path)[1].lower()
    if suffix == ".txt":
        text = _read_text_file(path)
        pages = [text]
    elif suffix == ".docx":
        from docx import Document
        doc = Document(path)
        text = "\n\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())
        pages = [text]
    elif suffix == ".pdf":
        try:
            import fitz
            pages = [page.get_text() for page in fitz.open(path)]
        except ImportError:
            from pypdf import PdfReader
            pages = [(p.extract_text() or "") for p in PdfReader(path).pages]
        text = "\n\n".join(pages)
    else:
        raise ValueError("Unsupported document type. Use PDF, DOCX or TXT.")
    return DocumentStore(name=name, text=text, pages=pages)


def answer_question(store, question, history=None, k=5):
    if store is None:
        raise ValueError("No document loaded.")
    text = store.text
    selected = []
    for chunk in store.chunks:
        if len(chunk.strip()) == 0:
            continue
        if question.lower() in chunk.lower() or any(word in chunk.lower() for word in question.lower().split() if len(word) > 3):
            selected.append(chunk)
    if not selected:
        selected = store.chunks[:k]
    context = "\n\n".join(selected)
    prompt = (
        "Use only the provided document text to answer the user's question. "
        "If the answer is not in the text, say so plainly.\n\n"
        f"Question: {question}\n\nDocument text:\n{context}"
    )
    answer = ask([{"role": "user", "content": prompt}], system="You are a careful document QA assistant.", max_tokens=700)
    return answer, list(range(1, min(len(store.chunks), k) + 1))


def summarize_document(store, max_chars=60000):
    if store is None:
        raise ValueError("No document loaded.")
    text = store.text[:max_chars]
    return ask([
        {"role": "user", "content": f"Summarize the following document in a concise but complete way.\n\n{text}"}
    ], system="You are a careful summarizer.", max_tokens=700)
