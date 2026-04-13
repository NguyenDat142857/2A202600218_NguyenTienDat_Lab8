import os
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text, chunk_size=200):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def get_embedding(text):
    return model.encode(text).tolist()

def build_index():
    client = chromadb.Client()
    collection = client.get_or_create_collection("rag_lab")

    data_path = "data/docs"
    for fname in os.listdir(data_path):
        with open(os.path.join(data_path, fname), "r", encoding="utf-8") as f:
            text = f.read()
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk],
                embeddings=[get_embedding(chunk)],
                ids=[f"{fname}_{i}"],
                metadatas=[{
                    "source": fname,
                    "section": f"chunk_{i}",
                    "effective_date": "2026"
                }]
            )
    print("Index built!")

if __name__ == "__main__":
    build_index()
