import sqlite3
from pathlib import Path

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

if __name__ == "__main__":
    from rich import print

    conn = open_db(":memory:")
    record = {
        "law": "LFT", 
        "article": "76", 
        "text": "Las personas trabajadoras..."
    }

    save(conn, record, b"\x00\x01")
    print(conn.execute("SELECT law, article, part, text FROM chunks").fetchall())

    save(conn, record, b"\x00\x01")