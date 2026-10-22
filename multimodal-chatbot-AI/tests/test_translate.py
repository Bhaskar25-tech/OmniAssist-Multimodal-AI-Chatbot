from modules.module7_translate import chunk_text


def test_chunking_keeps_all_text():
    text = "\n".join(f"line {i} " + "x" * 100 for i in range(200))
    chunks = chunk_text(text, size=1000)
    assert len(chunks) > 1
    assert all(len(c) <= 1200 for c in chunks)
    assert sum(c.count("line") for c in chunks) == 200
