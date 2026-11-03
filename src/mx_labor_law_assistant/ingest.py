import re
from pathlib import Path

import pypdf

def read_pdf(path: Path) -> list[str]:
    """Etapa 1: Un texto por página."""
    reader = pypdf.PdfReader(path)
    return  [page.extract_text() for page in reader.pages]
    
    
def clean_page(text: str) -> str:
    """Etapa 2: Eliminar encabezado y pie de página."""
    PATTERN = r"\d+ de \d+"
    match = re.search(PATTERN, text)
    if match is None:
        return text
    return text[match.end():]
    
def join_page(pages: list[str]) -> str:
    """Etapa 3: Un solo texto, para que ningñun artículo quede partido entre páginas."""
    cleaned = []
    for page in pages:
        cleaned.append(page)
    return "\n".join(cleaned)

def law_body(text: str, start: str, end:str) -> str:
    """Etapa 4: Obtener solo el intervalo """
    return text[text.find(start): text.find(end)]


if __name__ == "__main__":
    from rich import print
    PDF_LFT = 'data/laws/lft.pdf'
    PDF_CPEUM = 'data/laws/cpeum.pdf'
    pages = read_pdf(PDF_LFT)

    law = law_body(
        text=join_page(pages),
        start="Artículo 1o.",
        end="TRANSITORIOS"
    )
    print(law[:300])    
    print(law[-300:])


    """HEADER
    LEY FEDERAL DEL TRABAJO

    CÁMARA DE DIPUTADOS DEL H. CONGRESO DE LA UNIÓN
    Secretaría General
    Secretaría de Servicios Parlamentarios
    Última Reforma DOF 14-05-2026
    """

    """FOOTER
    20 de 457
    """

    """BODY
    ###
    """
  