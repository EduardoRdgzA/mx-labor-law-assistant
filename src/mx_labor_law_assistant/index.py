from .config import DB_PATH
from .ingest import load_records
from .retrieve import embed
from .store import open_db, save

def index(size: int = 100) -> None:
    """Etapa 1: Embebe los pedazos por lotes y los guarda"""
    records = load_records()
    conn = open_db(DB_PATH)
    
    for i in range(0, len(records), size):
        batch = records[i: i + size]
        vectors = embed([r["text"] for r in batch])
        for record, vector in zip(batch, vectors):
            save(conn, record, vector.tobytes())

if __name__ == "__main__":
    index()