import numpy as np
import requests
from typing import TypedDict
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END
from .models import DocumentChunk
from pgvector.django import MaxInnerProduct

print("Loading embedding model")
model = SentenceTransformer('all-MiniLM-L6-v2')

class GraphState(TypedDict):
    question: str
    context: str
    answer: str
    avg_similarity: float
    query_norm: float

def retrievenode(state: GraphState):
    question = state["question"]
    raw_vector = model.encode(question, normalize_embeddings=False)
    mu = np.mean(raw_vector)
    sigma = np.std(raw_vector)
    if sigma == 0: sigma = 1e-9
    query_vector = (raw_vector - mu) / sigma
    q_norm = np.linalg.norm(query_vector)
    top_chunks = DocumentChunk.objects.order_by(
        MaxInnerProduct('embedding', query_vector.tolist())
    )[:3]
    if not top_chunks:
        return {"context": "", "avg_similarity": 0.0, "query_norm": float(q_norm)}
    chunk_similarities = []
    for chunk in top_chunks:
        c_vec = np.array(chunk.embedding)
        c_norm = np.linalg.norm(c_vec)
        sim = np.dot(query_vector, c_vec) / (q_norm * c_norm) if q_norm != 0 else 0
        chunk_similarities.append(float(sim))
    avg_similarity = np.mean(chunk_similarities)
    context = "\n\n".join([chunk.text for chunk in top_chunks])
    return {
        "context": context,
        "avg_similarity": avg_similarity,
        "query_norm": float(q_norm)
    }

def generatenode(state: GraphState):
    question = state["question"]
    context = state["context"]
    if not context:
        return {"answer": "No context found"}
    prompt = f"Answer ONLY based on the context:\n\n{context}\n\nQuestion: {question}"
    try:
        ollama_res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False},
            timeout=30
        )
        ollama_res.raise_for_status()
        final_answer = ollama_res.json().get('response', 'Error')
    except requests.exceptions.RequestException as e:
        final_answer = f"Error: {str(e)}"
    return {"answer": final_answer}

print("Compiling workflow")
workflow = StateGraph(GraphState)
workflow.add_node("retrieve", retrievenode)
workflow.add_node("generate", generatenode)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)
rag_app = workflow.compile()