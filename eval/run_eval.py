import json

from src.mx_labor_law_assistant.config import DB_PATH, ROOT
from src.mx_labor_law_assistant.store import load_all, open_db
from src.mx_labor_law_assistant.retrieve import search

def load_questions() -> list[dict]:
    """Etapa 1: Lee las preguntas de prueba."""
    path = ROOT / "eval" / "questions.json"
    return json.loads(path.read_text(encoding="utf-8"))

def retrieve(questions: list[dict], records: list[dict], vectors, k:int = 5) -> list[list[tuple]]:
    """Etapa 2: Por cada pregunta, guarda los artículos que trae la búsqueda."""
    all_found = []
    for question in questions:
        results = search(question["question"], records, vectors, k)

        articles = []
        for result in results:
            articles.append((result["law"], result["article"]))

        all_found.append(articles)
    return all_found

def score(questions, all_found):
    """Etapa 3:Marca si algún artículo esperado está entre los que trae la búsqueda"""
    rows = []

    for i in range(len(questions)):
        question = questions[i]
        found = all_found[i]

        if question["expected"] == []:
            continue

        rank = None
        for expected in question["expected"]:
            key = (expected["law"], expected["article"])
            if key in found:
                position = found.index(key) + 1
                if rank is None or position < rank:
                    rank = position                

        rows.append({
            "id": question["id"],
            "status": rank is not None and rank <= 5,
            "rank": rank
        })

    return rows


if __name__ == "__main__":
    from rich import print

    questions = load_questions()
    records, vectors = load_all(open_db(DB_PATH))
    rows = score(questions, retrieve(questions, records, vectors, k=10))

    for row in rows:
        print(row["id"], row["status"], row["rank"])

    print(sum(row["status"] for row in rows), "de", len(rows) )