from .config import client, MODEL

INSTRUCTIONS = (
    "Eres un asistente de derecho laboral mexicano. "
    "Response solo con los artículos que se te dan. "
    "Cita el artículo y la ley donde sale cada dato. "
    "Si la respuesta no está en los artículos, notifícalo."
)


def ask(question: str, context: str) -> str:
    response = client.responses.create(
        model=MODEL,
        instructions=INSTRUCTIONS,
        input=f"Artículos:\n{context}\n\nPregunta: {question}",
    )
    return response.output_text

if __name__ == "__main__":
    from rich import print
    QUESTIONS = (
        "¿Cuántos días de vacaciones tiene un trabajador en México en su primer año?"
    )
    ARTICLE = (
        "Artículo 76.- Las personas trabajadoras que tengan más de un año de servicios disfrutarán de un periodo anual de vacaciones pagadas, que en ningún caso podrá ser inferior a doce días laborables, y que aumentará en dos días laborables, hasta llegar a veinte, por cada año subsecuente de servicios. "
        "A partir del sexto año, el periodo de vacaciones aumentará en dos días por cada cinco de servicios. "
        "Artículo reformado DOF 27-12-2022."
    )

    resp = ask(question=QUESTIONS, context= ARTICLE)
    print(resp)
