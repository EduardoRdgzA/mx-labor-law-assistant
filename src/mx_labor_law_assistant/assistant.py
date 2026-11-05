import numpy as np
from pathlib import Path

from .config import DB_PATH, USER_DB_PATH, langfuse, observe
from .generate import ask
from .retrieve import search
from .store import load_all, open_db
from .validate import validate
from .user_docs import add_documents

@observe(name="question")
def answer(question: str) -> str:
    """Etapa 1: Busca los artículos y le pide respuesta al modelo."""
    records, vectors = load_all(open_db(DB_PATH))
    user_records, user_vectors = load_all(open_db(USER_DB_PATH))

    if user_records:
        records = records + user_records
        vectors = np.vstack([vectors, user_vectors])

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

    import argparse
    from langfuse import propagate_attributes

    import uuid

    console  = Console()

    parser = argparse.ArgumentParser(description="Asistente de derechos laborales")
    parser.add_argument("--question", required=True, help="Realiza una pregunta")
    parser.add_argument("--docs", nargs="+", default=[], help="PDFs propios a cargar antes de preguntar")
    args = parser.parse_args()

    if args.docs:
        result = add_documents([Path(path) for path in args.docs])
        console.print("[green]Procesados", result["done"])
        console.print("[red]Fallaron", result["failed"])


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


    if args.question:
        session_id = uuid.uuid4().hex[:8]
        with propagate_attributes(session_id=session_id, tags=["assistant"]):
            assistant(args.question)
        console.print(f"\n[green]Session {session_id}")

    langfuse.flush()
    
    # test
    QN1 = (
        "¿Cuántos días de aguinaldo me corresponden y cuándo me lo tienen que pagar?"
    )

    QN2 = (
        "Llevo 4 años en una empresa con contrato por tiempo indeterminado y me despidieron sin causa "
        "justificada en Junio. ¿Qué opciones tengo y a qué indemnización tengo derecho? Además, "
        "¿me corresponde aguinaldo y prima vacacional de este año, aunque no lo haya trabajado completo?"
        )

    QN3 = "¿Qué mide la medida F1 de complejidad en un problema de clasificación?"


    