from .config import DB_PATH, langfuse, observe
from .generate import ask
from .retrieve import search
from .store import load_all, open_db
from .validate import validate

@observe(name="question")
def answer(question: str) -> str:
    """Etapa 1: Busca los artículos y le pide respuesta al modelo."""
    records, vectors = load_all(open_db(DB_PATH))
    found = search(question, records, vectors)
    context = "\n\n".join(
        f"{r['law']}, artículo {r['article']}:\n{r['text']}" for r in found
    )

    text = ask(question, context)

    check = validate(text, found)
    cited = set(check["cited"])
    sources =  [r for r in found if (r["law"], r["article"]) in cited]

    return {
        "answer": text,
        "sources": sources,
        "validation": check
    }

if __name__ == "__main__":
    from rich.console import Console
    from rich.markdown import Markdown
    from langfuse import propagate_attributes

    console  = Console()
    
    def assistant(question: dict) -> None:

        resp = answer(question)

        console.print(f"[green]Question")
        console.print(Markdown(question))

        console.print(f"\n[green]Answer")
        console.print(Markdown(resp["answer"]))

        console.print(f"\n[green]Sources")
        console.print(resp["sources"])

        console.print(f"\n[green]Validations")
        console.print(resp["validation"])

    QN1 = (
        "¿Cuántos días de aguinaldo me corresponden y cuándo me lo tienen que pagar?"
    )

    QN2 = (
        "Llevo 4 años en una empresa con contrato por tiempo indeterminado y me despidieron sin causa "
        "justificada en Junio. ¿Qué opciones tengo y a qué indemnización tengo derecho? Además, "
        "¿me corresponde aguinaldo y prima vacacional de este año, aunque no lo haya trabajado completo?"
        )
    with propagate_attributes(session_id="prueba-8", tags=["notebook"]):
        assistant(QN1)

    langfuse.flush()