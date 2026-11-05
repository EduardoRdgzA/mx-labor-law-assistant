from pathlib import Path

from .ingest import chunk, read_pdf


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


if __name__ == "__main__":
    import sys
    from rich import print

    records = load_document(Path(sys.argv[1]))
    print(len(records))
    print(records[0])