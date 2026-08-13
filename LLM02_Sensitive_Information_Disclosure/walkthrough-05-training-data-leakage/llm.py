import os

from ollama import Client


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")

client = Client(host=OLLAMA_HOST)


def generate(prompt: str, model: str = DEFAULT_MODEL) -> str:
    response = client.generate(
        model=model,
        prompt=prompt,
        options={
            "temperature": 0.2,
        },
    )

    return response["response"].strip()