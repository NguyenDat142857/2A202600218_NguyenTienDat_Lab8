import chromadb
from sentence_transformers import SentenceTransformer
import openai
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text):
    return model.encode(text).tolist()

def retrieve(query):
    client = chromadb.Client()
    collection = client.get_collection("rag_lab")
    results = collection.query(
        query_embeddings=[get_embedding(query)],
        n_results=3
    )
    return results["documents"][0]

def call_llm(context, question):
    prompt = f"""Answer only using context:
{context}

Question: {question}
"""
    return prompt  # placeholder

def rag_answer(question):
    docs = retrieve(question)
    if not docs:
        return {"answer": "Không đủ dữ liệu", "sources": []}

    context = "\n".join(docs)
    answer = call_llm(context, question)
    return {
        "answer": answer,
        "sources": docs
    }

if __name__ == "__main__":
    print(rag_answer("SLA xử lý ticket P1 là bao lâu?"))
