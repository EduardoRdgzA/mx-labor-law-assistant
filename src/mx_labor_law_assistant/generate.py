import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def ask(question: str) -> str:
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL"),
        input=question,
    )
    return response.output_text

if __name__ == "__main__":
    from rich import print
    QUESTIONS = (
        "¿Cuántos días de vacaciones tiene un trabajador en México en su primer año?"
    )
    resp = ask(QUESTIONS)
    print(resp)
