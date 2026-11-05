from pathlib import Path

from .ingest import chunk, read_pdf
from .config import USER_DB_PATH
from .retrieve import embed
from .store import open_db, save

def load_document(path: Path) -> list[dict]:
    """Etapa 1: De un PDF del usuario a registros, uno por página."""
    records = []

    for number, page in enumerate(read_pdf(path), start=1):
        lines = [" ".join(line.split()) for line in page.splitlines()]
        text = "\n".join(line for line in lines if line)

        if text:
            records.extend(chunk({
                "law": path.name,
                "article": f"p. {number}",
                "text": text,
            }))

    if not records:
        raise ValueError(f"{path.name}: no tiene texto (¿está escaneado?)")
    return records

def add_documents(paths: list[Path]) -> dict:
    """Etapa 2: Procesa cada PDF por separado; si uno falla, los demás siguen."""
    conn = open_db(USER_DB_PATH)
    done = []
    failed = []

    for path in paths:
        try:
            records = load_document(path)
            vectors = embed([r["text"] for r in records])
            for record, vector in zip(records, vectors):
                save(conn, record, vector.tobytes())
            done.append(path.name)
        except Exception as error:
            failed.append((path.name, str(error)))

    return {"done": done, "failed": failed}

if __name__ == "__main__":
    import sys
    from rich import print

    records = load_document(Path(sys.argv[1]))
    print(len(records))
    print(records[0])

    result = add_documents([Path(arg) for arg in sys.argv[1:]])
    print("Procesados:", result["done"])
    print("Fallaron:", result["failed"])