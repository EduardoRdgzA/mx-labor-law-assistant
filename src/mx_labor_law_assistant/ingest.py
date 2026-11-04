from .config import ROOT

import re
from pathlib import Path

import pypdf

def read_pdf(path: Path) -> list[str]:
    """Etapa 1: Un texto por página."""
    reader = pypdf.PdfReader(path)
    return  [page.extract_text(extraction_mode="layout") for page in reader.pages]

def clean_page(text: str) -> str:
    """Etapa 2: Eliminar encabezado y pie de página."""
    header = re.compile(
        r"Secretaría de Servicios Parlamentarios.*\n"
    )
    footer = re.compile(
        r"\d+ de \d+\s*$"
    )
    start = header.search(text).end() if header else 0
    end = footer.search(text).start() if footer else len(text)
    
    text = text[start: end]
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(lines)
    
def join_page(pages: list[str]) -> str:
    """Etapa 3: Un solo texto, para que ningñun artículo quede partido entre páginas."""    
    return "\n".join([clean_page(page) for page in pages])

def law_body(text: str, start: str, end:str) -> str:
    """Etapa 4: Obtener solo el intervalo """
    return text[text.find(start): text.find(end)]
      
def split_articles(body: str) -> list[str]:
    """Etapa 5: un pedazo por artículo, de un inicio al siguiente, sin título de capítulo."""
    article = re.compile(
        r"(?m)^Artículo \d"
    )
    heading_r = re.compile(
        r"(?m)^(T[IÍ]TULO|CAP[IÍ]TULO)"
    )
    positions = [match.start() for match in article.finditer(body)]
    positions.append(len(body))

    articles = []
    for a, b in zip(positions, positions[1:]):
        piece = body[a:b]
        heading = heading_r.search(piece)
        if heading:
            piece = piece[:heading.start()]
        articles.append(piece.strip())
    return articles


def article_number(piece:str) -> str:
    """Etapa 6: número del artículo"""
    # Artículo 512-D Bis.- ..."
    number = re.compile(
        r"Artículo (\d+)"           
        r"(?:o\.)?"                  
        r"(?: ?- ?([A-ZÑ])\b)?"      
        r"(?: (Bis|Ter|Quáter))?",   
    ) 
    
    match = number.match(piece)
    number, letter, suffix = match.groups()
    
    label = number
    if letter:
        label += f"-{letter}"
    if suffix:
        label += f" {suffix}"
    return label

def load_law(path: Path, law: str, start: str, end:str) -> list[dict]:
    """Etapa 7: De un PDF a una lista de registros """
    body = law_body(
        text=join_page(read_pdf(path)),
        start=start,
        end=end,
    )
    schema = lambda piece: {
        "law": law,
        "article": article_number(piece),
        "text": piece
    }
    return [schema(piece) for piece in split_articles(body)]

def chunk(record: dict, max_words: int = 400) -> list[dict]:
    """Etapa 8: Parte un artículo en pedazos de hasta 400 palabras"""
    if len(record["text"]. split()) <= max_words:
        return[record]

    chunks = []
    current = []
    for line in record["text"].splitlines():
        current.append(line)
        if len(" ".join(current).split()) >= max_words:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))
    
    schema = lambda i, text: {
        **record, 
        "text": text,
         "part": i + 1
        }
    
    return [schema(i, text) for i, text in enumerate(chunks)] 

def load_record() -> list[dict]:
    """Etapa 9: registos de as dos leyes, ya partidos."""
    lft = load_law(
        path=ROOT / "data" / "laws" / "lft.pdf",
        law="LFT",
        start="Artículo 1o.",
        end="TRANSITORIOS"
    )

    cpeum = load_law(
        path=ROOT / "data"/ "laws" / "cpeum.pdf",
        law="CPEUM",
        start="Artículo 123.",
        end="Artículo 124."
    )
    
    records = []
    for r in lft + cpeum:
        records.extend(chunk(r))
    return records

if __name__ == "__main__":
    from rich import print

    records = load_record()

    print(len(records))
    print(max(len(r["text"].split()) for r in records))   