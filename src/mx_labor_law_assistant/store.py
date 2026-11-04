import sqlite3
from pathlib import Path
import numpy as np

def open_db(path: Path) -> sqlite3.Connection:
    """Etapa 1: Abre la base y crea la tabla si no existe."""
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            law TEXT NOT NULL,
            article TEXT NOT NULL,
            part INTEGER NOT NULL,
            text TEXT NOT NULL,
            embedding BLOB NOT NULL,
            PRIMARY KEY (law, article, part)
        )
        """
    )
    return conn

def save(conn: sqlite3.Connection, record: dict, embedding: bytes) -> None:
    """Etapa 2: Guarda un pedazo con su embedding."""
    values = (
            record.get("law"),
            record.get("article"),
            record.get("part", 0),
            record.get("text"),
            embedding
        )
    
    conn.execute(
        """
        INSERT INTO chunks (law, article, part, text, embedding) 
        VALUES (?, ?, ?, ?, ?)
        """,
        values
    )
    conn.commit()

def load_all(conn: sqlite3.Connection) -> tuple[list[dict], np.ndarray]:
    """Etapa 3: Lee todos los pedazos y sus conectores, en el mismo orden."""
    rows = conn.execute(
        """
        SELECT law, article, part, text, embedding
        FROM chunks 
        ORDER BY rowid
        """
    ).fetchall()

    schema = lambda law, article, part, text: {
        "law": law,
        "article": article,
        "part": part,
        "text": text
    }

    records = [schema(law, article, part, text) for law, article, part, text, _ in rows]
    vectors = np.array([np.frombuffer(row[4], dtype=np.float32) for row in rows])

    return records, vectors

if __name__ == "__main__":
    from rich import print
    from .config import DB_PATH

    records, vectors = load_all(open_db(DB_PATH))
    print(records[-1:], vectors[-1:])

    print(len(records), vectors.shape, vectors.dtype)
    print(records[0]["law"], records[0]["article"], records[0]["part"])