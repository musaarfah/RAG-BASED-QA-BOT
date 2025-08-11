# vector_store_builder.py

import os
from ingest import extract_text
from embedder import chunk_text, embed_chunks, save_to_faiss

DOCS_FOLDER = "data/documents"
FAISS_PATH = "data/faiss_index/company_docs.index"
META_PATH = "data/faiss_index/company_docs.pkl"

all_embeddings = []
all_texts = []
all_metadata = []

for filename in os.listdir(DOCS_FOLDER):
    file_path = os.path.join(DOCS_FOLDER, filename)

    if not os.path.isfile(file_path):
        continue  # skip non-files

    print(f"🔍 Processing {filename}...")
    try:
        text = extract_text(file_path)
        chunks = chunk_text(text)
        embeddings, chunk_texts = embed_chunks(chunks)

        # Attach metadata (e.g. filename)
        metadata = [{"source": filename} for _ in chunk_texts]

        all_embeddings.extend(embeddings)
        all_texts.extend(chunk_texts)
        all_metadata.extend(metadata)

    except Exception as e:
        print(f"❌ Failed to process {filename}: {e}")

# Save all embeddings to one FAISS index
save_to_faiss(
    all_embeddings,
    all_texts,
    faiss_path=FAISS_PATH,
    metadata_path=META_PATH,
    metadata=all_metadata
)

print("✅ Vector DB created with all documents.")
