import numpy as np

from .config import client, EMBEDDING

def embed(texts: list[str]) -> np.ndarray:
    """Etapa 1: Convierte textos en vectores, en el mismo orden"""
    response = client.embeddings.create(
        model=EMBEDDING,
        input=texts,
    )
    return np.array([item.embedding for item in response.data], dtype=np.float32)

def search(
    questions: str, 
    records: list[dict],
    vectors: np.ndarray,
    k: int = 5
) -> list[dict]:
    """Etapa 2: Devuelve los k vecinos más parecidos a la pregunta."""
    query = embed([questions])[0]
    scores = vectors @ query
    best = np.argsort(scores)[::-1][:k]
    
    schema = lambda i: {
        **records[i],
        "score": float(scores[i])
    }
    return [schema(i) for i in best]

if __name__ == "__main__":
    from rich import print
    from .config import DB_PATH
    from .store import load_all, open_db
    
    records, vectors = load_all(open_db(DB_PATH))
    print(abs(float((vectors[0] ** 2).sum()) - 1) < 0.01)

    question = "¿Cuántos días de vacaciones tiene un trabajador en su primer año?"
    
    print("law", "article", "part", "score")
    for r in search(question, records, vectors):
        print(r["law"], r["article"], r["part"], round(r["score"], 3))
