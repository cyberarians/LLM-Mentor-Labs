import os

import streamlit as st
from dotenv import load_dotenv

from extraction import ProgressiveExtractor
from guards import apply_output_guard
from llm import generate_response
from prompts import build_messages


load_dotenv()


APP_NAME = os.getenv(
    "APP_NAME",
    "SentinelShield Fraud Detection Assistant",
)

DEFAULT_MODE = os.getenv(
    "LAB_MODE",
    "vulnerable",
).strip().lower()

if DEFAULT_MODE not in {"vulnerable", "secure"}:
    DEFAULT_MODE = "vulnerable"


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛡️",
    layout="wide",
)


def initialize_session() -> None:
    """Initialize the lab session state."""

    if "mode" not in st.session_state:
        st.session_state.mode = DEFAULT_MODE

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "extractor" not in st.session_state:
        st.session_state.extractor = ProgressiveExtractor()

    if "transaction" not in st.session_state:
        st.session_state.transaction = {
            "transaction_amount": 8500.0,
            "location": "New York",
            "device_risk": "MEDIUM",
            "velocity": "HIGH",
            "behavioral_anomaly": 40,
        }


def reset_lab() -> None:
    """Reset the current lab session."""

    st.session_state.messages = []
    st.session_state.extractor.reset()

    st.session_state.transaction = {
        "transaction_amount": 8500.0,
        "location": "New York",
        "device_risk": "MEDIUM",
        "velocity": "HIGH",
        "behavioral_anomaly": 40,
    }


def get_transaction_context() -> str:
    """Build transaction context for the LLM."""

    transaction = st.session_state.transaction

    return f"""
Transaction Details:

- Transaction Amount: ${transaction["transaction_amount"]:,.2f}
- Location: {transaction["location"]}
- Device Risk: {transaction["device_risk"]}
- Transaction Velocity: {transaction["velocity"]}
- Behavioral Anomaly Score: {transaction["behavioral_anomaly"]}/100
""".strip()


def process_message(user_message: str) -> str:
    """Process a user message through the lab pipeline."""

    st.session_state.extractor.analyze(user_message)

    contextual_message = (
        f"{get_transaction_context()}\n\n"
        f"User Request:\n{user_message}"
    )

    messages = build_messages(
        user_message=contextual_message,
        mode=st.session_state.mode,
    )

    raw_response = generate_response(
        messages=messages,
        temperature=0.2,
    )

    guard_result = apply_output_guard(
        response=raw_response,
        mode=st.session_state.mode,
    )

    return guard_result.content


def render_sidebar() -> None:
    """Render lab configuration controls."""

    with st.sidebar:
        st.header("Lab Configuration")

        secure_mode = st.toggle(
            "Secure Mode",
            value=st.session_state.mode == "secure",
            help=(
                "Switch between the vulnerable and "
                "mitigated configurations."
            ),
        )

        selected_mode = (
            "secure"
            if secure_mode
            else "vulnerable"
        )

        if selected_mode != st.session_state.mode:
            st.session_state.mode = selected_mode
            st.session_state.messages = []
            st.session_state.extractor.reset()
            st.rerun()

        st.divider()

        if st.session_state.mode == "secure":
            st.success("🟢 Secure Mode")
            st.caption(
                "Proprietary implementation details are "
                "restricted and output protection is enabled."
            )
        else:
            st.error("🔴 Vulnerable Mode")
            st.caption(
                "The model has access to proprietary "
                "fraud-detection context."
            )

        st.divider()

        if st.button(
            "Reset Lab",
            use_container_width=True,
        ):
            reset_lab()
            st.rerun()


def render_transaction_panel() -> None:
    """Render transaction input controls."""

    st.subheader("Transaction Details")

    transaction = st.session_state.transaction

    amount = st.number_input(
        "Transaction Amount",
        min_value=0.0,
        value=float(transaction["transaction_amount"]),
        step=100.0,
    )

    location = st.text_input(
        "Location",
        value=transaction["location"],
    )

    device_risk_options = ["LOW", "MEDIUM", "HIGH"]

    device_risk = st.selectbox(
        "Device Risk",
        device_risk_options,
        index=device_risk_options.index(
            transaction["device_risk"]
        ),
    )

    velocity_options = ["LOW", "MEDIUM", "HIGH"]

    velocity = st.selectbox(
        "Transaction Velocity",
        velocity_options,
        index=velocity_options.index(
            transaction["velocity"]
        ),
    )

    behavioral_anomaly = st.slider(
        "Behavioral Anomaly",
        min_value=0,
        max_value=100,
        value=int(transaction["behavioral_anomaly"]),
    )

    st.session_state.transaction = {
        "transaction_amount": amount,
        "location": location,
        "device_risk": device_risk,
        "velocity": velocity,
        "behavioral_anomaly": behavioral_anomaly,
    }


def render_chat() -> None:
    """Render the full-width interactive assistant."""

    st.subheader("Fraud Detection Assistant")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input(
        "Ask the assistant..."
    )

    if not user_message:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                response = process_message(user_message)

            except Exception as exc:
                response = (
                    "Unable to process the request. "
                    "Please verify that Ollama is running "
                    "and the configured model is available.\n\n"
                    f"Error: `{exc}`"
                )

        st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )


def render_header() -> None:
    """Render the lab header."""

    st.title(
        "🛡️ SentinelShield Fraud Detection Assistant"
    )

    st.caption(
        "LLM02 — Proprietary Algorithm & "
        "Intellectual Property Exposure"
    )

    st.write(
        "Analyze transactions and interact with the "
        "fraud-detection assistant."
    )


def main() -> None:
    """Application entry point."""

    initialize_session()

    render_sidebar()
    render_header()

    st.divider()

    # Transaction inputs occupy the full available width.
    render_transaction_panel()

    st.divider()

    # Chat occupies the full available width.
    render_chat()


if __name__ == "__main__":
    main()