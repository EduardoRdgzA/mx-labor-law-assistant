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
    heading = re.compile(
        r"(?m)^(T[IÍ]TULO|CAP[IÍ]TULO)"
    )
    positions = [match.start() for match in article.finditer(body)]
    positions.append(len(body))
    pieces = [body[a:b] for a, b in zip(positions, positions[1:])]

    heading_start = heading.search(body).start()
    articles = [piece[:heading_start].strip() for piece in pieces]
    
    return articles


def article_number(piece:str) -> str:
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

if __name__ == "__main__":
    from rich import print

    root = Path(__file__).resolve().parents[2]
    PDF_LFT = root / "data" / "laws" / "lft.pdf"
    PDF_CPEUM = root / "data"/ "laws" / "cpeum.pdf"
     
    pages = read_pdf(
        path=PDF_LFT
    )
    law = law_body(
        text=join_page(pages),
        start="Artículo 1o.",
        end="TRANSITORIOS"
    )
    
    articles = split_articles(law)
    numbers = [article_number(article) for article in articles]

    print(law.count("Secretaría de Servicios Parlamentarios"))     
    