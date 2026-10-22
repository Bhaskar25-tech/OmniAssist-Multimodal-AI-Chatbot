"""Shared LLM adapter. Defaults to free local Ollama; Anthropic is optional."""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2") if PROVIDER == "ollama" else os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
_client = None


def ask(messages, system=None, max_tokens=1500):
    """Generate text using Ollama locally or Anthropic when explicitly selected."""
    if PROVIDER == "ollama":
        try:
            import ollama
        except ImportError as exc:
            raise RuntimeError("Ollama Python package missing. Run: pip install ollama") from exc
        payload = []
        if system:
            payload.append({"role": "system", "content": system})
        for item in messages:
            content = item.get("content", "")
            # This helper is for text; image inputs use ask_vision below.
            if not isinstance(content, str):
                content = str(content)
            payload.append({"role": item.get("role", "user"), "content": content})
        try:
            response = ollama.chat(model=MODEL, messages=payload, options={"num_predict": max_tokens})
        except Exception as exc:
            raise RuntimeError(
                f"Could not connect to Ollama/model '{MODEL}'. Start Ollama and run `ollama pull {MODEL}`. Details: {exc}"
            ) from exc
        return response["message"]["content"].strip()

    if PROVIDER == "anthropic":
        global _client
        if _client is None:
            from anthropic import Anthropic
            key = os.getenv("ANTHROPIC_API_KEY", "").strip()
            if not key or key.startswith(("your_key", "PASTE_")):
                raise RuntimeError("ANTHROPIC_API_KEY is missing or still a placeholder in .env.")
            _client = Anthropic(api_key=key)
        kwargs = dict(model=MODEL, max_tokens=max_tokens, messages=messages)
        if system:
            kwargs["system"] = system
        return _client.messages.create(**kwargs).content[0].text.strip()

    raise RuntimeError("Invalid LLM_PROVIDER. Set it to 'ollama' or 'anthropic' in .env.")


def ask_vision(image_path, question="Describe this image.", system=None, max_tokens=700):
    """Use a local vision model for actual image understanding; OCR is handled separately."""
    if PROVIDER != "ollama":
        # Anthropic vision support can be added separately; do not pretend OCR is image understanding.
        raise RuntimeError("Direct image understanding currently requires LLM_PROVIDER=ollama and an Ollama vision model.")
    try:
        import ollama
        response = ollama.chat(
            model=os.getenv("OLLAMA_VISION_MODEL", "qwen2.5vl:3b"),
            messages=[{"role": "system", "content": system or "You are an accurate image understanding assistant."},
                      {"role": "user", "content": question, "images": [image_path]}],
            options={"num_predict": max_tokens},
        )
        return response["message"]["content"].strip()
    except Exception as exc:
        raise RuntimeError(
            "Image model unavailable. Run `ollama pull qwen2.5vl:3b` and ensure Ollama is running. " + str(exc)
        ) from exc
