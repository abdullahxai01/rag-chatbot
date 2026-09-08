import os
from pypdf import PdfReader
from docx import Document


def extract_text(file_path: str, filename: str) -> str:

    extension = os.path.splitext(filename)[1].lower()

    if extension == ".pdf":
        return extract_pdf(file_path)

    elif extension == ".docx":
        return extract_docx(file_path)

    elif extension == ".txt":
        return extract_txt(file_path)

    else:
        raise ValueError(
            "Unsupported file type. Please upload PDF, DOCX, or TXT."
        )


def extract_pdf(file_path: str) -> str:

    reader = PdfReader(file_path)

    text = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n\n".join(text)


def extract_docx(file_path: str) -> str:

    document = Document(file_path)

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n\n".join(text)


def extract_txt(file_path: str) -> str:

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

