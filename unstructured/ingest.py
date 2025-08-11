# This file is made to handle docs (pdf/docx/etc)

# ingest.py

# ingest.py

import fitz  # PyMuPDF
from docx import Document
import pypandoc
import os

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_odt(file_path):
    return pypandoc.convert_file(file_path, 'plain', format='odt')

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_text(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endswith(".odt"):
        return extract_text_from_odt(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format")

# Example usage
if __name__ == "__main__":
    text = extract_text("data/documents/UserStories-FYP-doc.odt")
    print(text[:1000])  # Print first 1000 characters
