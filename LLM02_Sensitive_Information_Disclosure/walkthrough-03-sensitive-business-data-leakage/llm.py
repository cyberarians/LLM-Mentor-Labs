import os

import ollama
from dotenv import load_dotenv


load_dotenv()

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://host.docker.internal:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b",
)

client = ollama.Client(host=OLLAMA_HOST)


def generate_response(prompt):
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]