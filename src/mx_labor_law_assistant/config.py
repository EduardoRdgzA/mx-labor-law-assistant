from pathlib import Path
import os

from dotenv import load_dotenv
from langfuse import get_client, observe
from openai import OpenAI

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "laws.sqlite"

MODEL = os.getenv("OPENAI_MODEL")
EMBEDDING = os.getenv("OPENAI_EMBEDDING_MODEL")

client = OpenAI()
langfuse = get_client()
