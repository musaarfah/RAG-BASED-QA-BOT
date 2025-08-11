# vector_store_incremental.py

import os
import pickle
import faiss
import numpy as np
from ingest import extract_text
from embedder import chunk_text, embed_chunks

# ==== CONFIG ====
DOCS_FOLDER = "data/documents"  # folder with all your PDFs/DOCs
FAISS_PATH = "data/faiss_index/company_docs.index"
META_PATH = "data/faiss_index/company_docs.pkl"
# ================

# Load existing FAISS index & metadata if they exist
if os.path.exists(FAISS_PATH) and os.path.exists(META_PATH):
    print("📂 Loading existing FAISS index...")
    index = faiss.read_index(FAISS_PATH)

    with open(META_PATH, "rb") as f:
        meta_data = pickle.load(f)
    all_texts = meta_data["texts"]
    all_metadata = meta_data["metadata"]

    processed_files = {m["source"] for m in all_metadata if "source" in m}
else:
    print("🆕 No existing index found. Creating a new one...")
    index = None
    all_texts = []
    all_metadata = []
    processed_files = set()

# Go through documents and find unprocessed ones
new_files = [
    f for f in os.listdir(DOCS_FOLDER)
    if os.path.isfile(os.path.join(DOCS_FOLDER, f)) and f not in processed_files
]

if not new_files:
    print("✅ No new documents to process.")
else:
    print(f"📄 Found {len(new_files)} new document(s) to process: {new_files}")

    all_new_embeddings = []
    all_new_texts = []
    all_new_metadata = []

    for filename in new_files:
        file_path = os.path.join(DOCS_FOLDER, filename)
        try:
            print(f"🔍 Processing {filename}...")
            text = extract_text(file_path)
            chunks = chunk_text(text)
            embeddings, chunk_texts = embed_chunks(chunks)

            # Attach metadata
            metadata = [{"source": filename} for _ in chunk_texts]

            all_new_embeddings.extend(embeddings)
            all_new_texts.extend(chunk_texts)
            all_new_metadata.extend(metadata)
        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}")

    # Update FAISS index
    if all_new_embeddings:
        new_embeddings_np = np.array(all_new_embeddings).astype("float32")

        if index is None:
            # Create new FAISS index
            dim = len(new_embeddings_np[0])
            index = faiss.IndexFlatL2(dim)

        index.add(new_embeddings_np)

        # Append new data to metadata lists
        all_texts.extend(all_new_texts)
        all_metadata.extend(all_new_metadata)

        # Save updated FAISS index
        faiss.write_index(index, FAISS_PATH)

        # Save updated metadata
        with open(META_PATH, "wb") as f:
            pickle.dump({"texts": all_texts, "metadata": all_metadata}, f)

        print(f"✅ Added {len(all_new_texts)} new chunks to the index.")
    else:
        print("⚠ No new embeddings generated.")
