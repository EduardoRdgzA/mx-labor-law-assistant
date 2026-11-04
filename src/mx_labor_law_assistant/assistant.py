from .config import DB_PATH
from .generate import ask
from .retrieve import search
from .store import load_all, open_db

def answer(question: str) -> str:
    """Etapa 1: Busca los artículos y le pide respuesta al modelo."""
    records, vectors = load_all(open_db(DB_PATH))
    found = search(question, records, vectors)
    context = "\n\n".join(
        f"{r['law']}, artículo {r['article']}:\n{r['text']}" for r in found
    )
    return ask(question, context)

if __name__ == "__main__":
    from rich.console import Console
    from rich.markdown import Markdown
    console  = Console()
    
    ans = answer("¿Cuántos días de vacaciones tiene un trabajador en su primer año?")
    console.print(Markdown(ans))