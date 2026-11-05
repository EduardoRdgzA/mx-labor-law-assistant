from .config import client, langfuse, observe, MODEL

INSTRUCTIONS = (
    "Eres un asistente de derecho laboral mexicano. "
    "Responde solo con los fragmentos que se te dan. "
    "Da una respuesta completa: el dato principal, y las condiciones o "
    "excepciones que aparezcan en los fragmentos. "
    "Si varios fragmentos dan reglas distintas, di a qué caso aplica cada una; "
    "si el fragmento no lo dice, no lo supongas. "
    "Si la ley y un documento del usuario hablan del mismo tema, di qué dice cada uno. "
    "Cada fragmento empieza con un id entre corchetes, por ejemplo [F1]. "
    "Cita cada dato solo con ese id, al final de la frase: [F1]. "
    "Si un dato viene de dos fragmentos, pon un id por corchete: [F1][F3]. "
    "No escribas nombres de archivo, páginas ni artículos como cita. "
    "Si la respuesta no está en los fragmentos, dilo, no la inventes y no pongas citas."
)

@observe(name="LLM", as_type="generation")
def ask(question: str, context: str) -> str:
    response = client.responses.create(
        model=MODEL,
        instructions=INSTRUCTIONS,
        input=f"Artículos:\n{context}\n\nPregunta: {question}",
    )

    langfuse.update_current_generation(
        model=MODEL,
        usage_details={
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        },
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
