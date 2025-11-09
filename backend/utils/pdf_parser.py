from typing import List, Tuple
import PyPDF2


def extract_text_from_pdf(file_stream) -> str:
    """
    Extract all text from a PDF file stream using PyPDF2.
    Returns the raw string contents.
    """
    reader = PyPDF2.PdfReader(file_stream)
    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''
    return text


def extract_text_from_txt(file_stream) -> str:
    """
    Extract all text from a TXT file stream.
    Returns the raw string contents.
    """
    file_stream.seek(0)
    return file_stream.read().decode('utf-8')


def chunk_text(text: str, max_chunk_len: int = 500) -> List[str]:
    """
    Splits input text into overlapping chunks for embedding & retrieval.
    - max_chunk_len: Max chars per chunk (tunable for vector DB efficiency)
    Overlaps can help with answer completeness.
    """
    chunks = []
    stride = int(max_chunk_len * 0.75)  # 25% overlap
    for i in range(0, len(text), stride):
        chunk = text[i:i+max_chunk_len]
        if chunk:
            chunks.append(chunk)
    return chunks
