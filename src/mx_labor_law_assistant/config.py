from pathlib import Path
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

MODEL = os.getenv("OPENAI_MODEL")
EMBEDDING = os.getenv("OPENAI_EMBEDDING_MODEL")
DB_PATH = ROOT / "data" / "laws.sqlite"
