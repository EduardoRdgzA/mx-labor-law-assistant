import json
from pathlib import Path

from src.mx_labor_law_assistant.config import DB_PATH, ROOT
from src.mx_labor_law_assistant.store import load_all, open_db
from src.mx_labor_law_assistant.retrieve import search, embed
from src.mx_labor_law_assistant.assistant import answer

import numpy as np
from src.mx_labor_law_assistant.user_docs import load_document

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


def save_report(rows: list[dict], no_answer: list[dict]) -> Path:
    """Etapa 4: Guarda el resultado de la evaluación en eval/results/."""
    path = ROOT / "eval" / "results" / "retrieval.json"
    path.parent.mkdir(exist_ok=True)

    report = {
        "hits": sum([row["status"] for row in rows]),
        "total": len(rows),
        "rows": rows,
        "no_answer": no_answer,
    }
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path

def check_no_answer(questions: list[dict]) -> list[dict]:
    """Etapa 5: Hace preguntas sin respesuta a asistente y guarda la respuesta"""
    rows = []

    for question in questions:
        if question["expected"] != []:
            continue

        result = answer(question["question"])
        rows.append({
            "id": question["id"],
            "answer": result["answer"],
            "cited": result["validation"]["cited"]
        })

    return rows


if __name__ == "__main__":
    from rich import print

    questions = load_questions()
    records, vectors = load_all(open_db(DB_PATH))

    example = load_document(ROOT / "data" / "examples" / "lineamientos_ccl_cdmx.pdf")
    records = records + example
    vectors = np.vstack([vectors, embed([r["text"] for r in example])])

    rows = score(questions, retrieve(questions, records, vectors, k=10))
    no_answer = check_no_answer(questions)
    path = save_report(rows, no_answer)

    for row in rows:
        print(row["id"], row["status"], row["rank"])

    print(sum(row["status"] for row in rows), "de", len(rows))

    print("\nPreguntas sin respuesta")
    for row in no_answer:
        print("\n", row["id"], "| citó:", row["cited"])
        print(row["answer"])

    print("\nReporte:", path)