import io

from pypdf import PdfReader


def extract_text(content: bytes, content_type: str) -> str:
    """PDFs are binary-structured (compressed streams, font tables, xref
    tables) - decoding the raw bytes as UTF-8 produces mostly garbage with
    only stray literal fragments surviving. Real PDF text extraction here;
    text/plain and text/markdown are already real text, just decode."""
    if content_type == "application/pdf":
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return content.decode("utf-8", errors="ignore")
