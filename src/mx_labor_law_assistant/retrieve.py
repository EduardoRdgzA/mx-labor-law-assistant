import numpy as np

from .config import client, EMBEDDING

def embed(texts: list[str]) -> np.ndarray:
    """Etapa 1: Convierte textos en vectores, en el mismo orden"""
    response = client.embeddings.create(
        model=EMBEDDING,
        input=texts,
    )
    return np.array([item.embedding for item in response.data], dtype=np.float32)


if __name__ == "__main__":
    from rich import print
    
    em = embed(["Hola", "Mundo!"])

    print(em)