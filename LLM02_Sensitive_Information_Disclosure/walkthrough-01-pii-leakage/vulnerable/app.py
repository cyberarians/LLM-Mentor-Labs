import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from ollama import Client


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

client = Client(host=OLLAMA_HOST or "http://localhost:11434")


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

DATA_FILE = PROJECT_ROOT / "data" / "customer_data.json"
SYSTEM_PROMPT_FILE = CURRENT_DIR / "system_prompt.txt"


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

@st.cache_data
def load_customer_data():
    """Load customer records."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data
def load_system_prompt():
    """Load vulnerable system prompt."""
    with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as file:
        return file.read()


def build_prompt(system_prompt, customer_data, user_query):
    """Build the final prompt sent to the LLM."""

    return f"""
================ SYSTEM PROMPT ================

{system_prompt}

================ CUSTOMER RECORDS ================

{json.dumps(customer_data, indent=4)}

================ USER QUESTION ================

{user_query}

=================================================
"""


def query_llm(prompt):
    """Send prompt to Ollama."""

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------

st.set_page_config(
    page_title="LLMentor - Walkthrough 01",
    page_icon="🔐",
    layout="centered"
)

st.title("🔐 SecureBank AI")
st.subheader("Walkthrough 01: Personal Identifiable Information (PII) Leakage")

st.write(
    "Interact with the AI-powered customer support assistant and observe how sensitive customer information can be unintentionally disclosed."
)

user_query = st.text_area(
    "Enter your question",
    height=120
)

if st.button("Submit"):

    if not user_query.strip():
        st.warning("Please enter a question.")
        st.stop()

    try:

        customer_data = load_customer_data()
        system_prompt = load_system_prompt()

        final_prompt = build_prompt(
            system_prompt,
            customer_data,
            user_query
        )

        response = query_llm(final_prompt)

        st.markdown("### Response")
        st.success(response)

    except Exception as error:

        st.error(
f"""
Unable to connect to the AI assistant.

Please verify the following:

• Ollama is installed and running.
• The required model is available.
• The .env configuration is correct.

Technical Details:

{error}
"""
        )