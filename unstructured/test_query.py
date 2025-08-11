# test_query.py

import faiss
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np

# Load the FAISS index
index = faiss.read_index("data/faiss_index/company_docs.index")

# Load metadata
with open("data/faiss_index/company_docs.pkl", "rb") as f:
    data = pickle.load(f)
    texts = data["texts"]
    metadata = data["metadata"]

# Embed a sample query
query = "What is FatRat?"
model = SentenceTransformer("all-MiniLM-L6-v2")
query_embedding = model.encode([query]).astype("float32")

# Search
k = 3
distances, indices = index.search(query_embedding, k)

for i, idx in enumerate(indices[0]):
    print(f"\n🔹 Result {i+1}")
    print(f"📄 Source: {metadata[idx]['source']}")
    print(f"🧠 Chunk: {texts[idx]}")
    print(f"📏 Distance: {distances[0][i]}")
