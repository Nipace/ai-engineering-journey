from io import BytesIO
from pypdf import PdfReader

def extract_text_from_pdf(file_content: bytes) -> tuple[str, int]:
    """Extract text and page count from PDF bytes."""
    reader = PdfReader(BytesIO(file_content))

    extracted_pages: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        extracted_pages.append(page_text.strip())

    full_text = "\n\n".join(page_text for page_text in extracted_pages if page_text)

    return full_text, len(reader.pages)