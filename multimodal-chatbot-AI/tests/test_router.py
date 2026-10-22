from core.router import route


def test_image_goes_to_image_module():
    assert route("what is this?", has_image=True) == "image"


def test_image_with_translate_request():
    assert route("translate the text in this image to Hindi", has_image=True) == "translate"


def test_long_text_goes_to_summarize():
    assert route("some long text " * 200, has_long_text=True) == "summarize"


def test_translate_keyword():
    assert route("translate good morning to Telugu") == "translate"


def test_document_loaded_goes_to_document():
    assert route("what is the conclusion?", has_document=True) == "document"


def test_image_beats_document():
    assert route("explain this", has_image=True, has_document=True) == "image"
