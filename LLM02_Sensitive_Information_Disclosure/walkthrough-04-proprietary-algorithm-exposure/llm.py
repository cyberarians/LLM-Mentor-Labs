import os

import ollama
from dotenv import load_dotenv


load_dotenv()


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b"
)


client = ollama.Client(
    host=OLLAMA_BASE_URL
)


def generate_response(
    messages: list[dict[str, str]],
    temperature: float = 0.2,
) -> str:
    """
    Generate a response from the configured local Ollama model.
    """

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=messages,
        options={
            "temperature": temperature
        }
    )

    return response["message"]["content"]