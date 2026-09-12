import io

from pypdf import PdfWriter

from app.services.text_extraction import extract_text


def _blank_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_extract_text_plain_text_decodes_directly():
    assert extract_text(b"hello world", "text/plain") == "hello world"


def test_extract_text_markdown_decodes_directly():
    assert extract_text(b"# heading\n\nbody", "text/markdown") == "# heading\n\nbody"


def test_extract_text_pdf_does_not_raise_and_returns_string():
    # A blank page has no text - this asserts the pypdf path actually runs
    # (parses real PDF structure) without crashing, not that it produces
    # non-empty output for a page with nothing on it.
    result = extract_text(_blank_pdf_bytes(), "application/pdf")

    assert isinstance(result, str)


def test_extract_text_pdf_does_not_naively_utf8_decode_binary():
    pdf_bytes = _blank_pdf_bytes()

    result = extract_text(pdf_bytes, "application/pdf")

    # A naive UTF-8 decode of real PDF bytes would include the literal
    # "%PDF-" header text mixed with binary garbage - real extraction
    # shouldn't surface that raw structural marker as content.
    assert "%PDF-" not in result
