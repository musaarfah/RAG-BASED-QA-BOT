#  chunk the text


# embedder.py

from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import os
import pickle
import numpy as np

def chunk_text(text, chunk_size=500, chunk_overlap=50):
    """
    Splits text into overlapping chunks to fit within LLM context limits.

    Args:
        text (str): Full extracted text from a document.
        chunk_size (int): Target size of each chunk (characters).
        chunk_overlap (int): Overlap between chunks to preserve context.

    Returns:
        List[str]: List of text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],  # priority of where to split
    )
    chunks = splitter.split_text(text)
    return chunks

def embed_chunks(chunks, model_name="all-MiniLM-L6-v2"):
    """
    Generates embeddings for each chunk using a sentence transformer.

    Returns:
        embeddings: List of vectors
        chunks: Original text chunks
    """
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings, chunks


def save_to_faiss(embeddings, chunk_texts, faiss_path, metadata_path, metadata=None):
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)

    index.add(np.array(embeddings).astype('float32'))

    faiss.write_index(index, faiss_path)


    with open(metadata_path, 'wb') as f:
        pickle.dump({
            "texts": chunk_texts,
            "metadata": metadata
        }, f)