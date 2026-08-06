import os

import ollama
from dotenv import load_dotenv

from prompts import (
    VULNERABLE_SYSTEM_PROMPT,
    SECURE_SYSTEM_PROMPT,
)

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

client = ollama.Client(host=OLLAMA_HOST)


def generate_response(user_message: str, mode: str) -> str:
    """
    Generate a response from the LLM based on the selected protection mode.

    Args:
        user_message: User's input message.
        mode: "Vulnerable" or "Secure"

    Returns:
        Assistant response.
    """

    system_prompt = (
        VULNERABLE_SYSTEM_PROMPT
        if mode == "Vulnerable"
        else SECURE_SYSTEM_PROMPT
    )

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
    )

    return response["message"]["content"]