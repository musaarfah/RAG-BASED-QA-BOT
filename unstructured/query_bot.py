# query_bot.py

import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# ==== CONFIG ====
FAISS_PATH = "data/faiss_index/company_docs.index"
META_PATH = "data/faiss_index/company_docs.pkl"
EMBED_MODEL = "all-MiniLM-L6-v2"   # Embedding model for retrieval
HF_MODEL = "google/flan-t5-base"   # Free Hugging Face LLM
TOP_K = 3
# ================

# Load FAISS index
index = faiss.read_index(FAISS_PATH)

# Load metadata
with open(META_PATH, "rb") as f:
    meta_data = pickle.load(f)
all_texts = meta_data["texts"]
all_metadata = meta_data["metadata"]

# Load embedding model
embedder = SentenceTransformer(EMBED_MODEL)

# Load Hugging Face model pipeline
generator = pipeline("text2text-generation", model=HF_MODEL)

def retrieve(query, k=TOP_K):
    """Retrieve top-k chunks from FAISS."""
    query_vec = embedder.encode([query], convert_to_numpy=True).astype("float32")
    distances, indices = index.search(query_vec, k)
    
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        results.append({
            "text": all_texts[idx],
            "source": all_metadata[idx]["source"],
            "distance": float(dist)
        })
    return results

def generate_answer(question, context_chunks):
    """Use Hugging Face model to generate an answer based on retrieved context."""
    context_text = "\n\n".join([c["text"] for c in context_chunks])
    
    prompt = f"""
You are a helpful and engaging assistant. 
Answer the question **only** using the provided context below. 
If the context does not contain enough information to fully answer, 
politely explain that the exact answer is not available, 
then provide the closest relevant information from the context 
and/or suggest how the user could rephrase their question.

Question: {question}

Context:
{context_text}

Answer:
"""
    response = generator(prompt, max_length=200, truncation=True)
    return response[0]["generated_text"]

if __name__ == "__main__":
    while True:
        query = input("\n❓ Enter your question (or type 'exit' to quit): ")
        if query.lower() in ["exit", "quit"]:
            break
        
        # 1. Retrieve from FAISS
        results = retrieve(query)
        
        # 2. Generate synthesized answer
        answer = generate_answer(query, results)
        
        # 3. Print answer
        print("\n💡 Answer:")
        print(answer)
        
        # 4. Show sources and distances
        print("\n📚 Sources:")
        for r in results:
            print(f" - {r['source']} (distance: {r['distance']:.4f})")
