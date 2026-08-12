import os

import streamlit as st
from dotenv import load_dotenv

from guards import apply_output_guard
from llm import generate_response
from prompts import build_prompt
from retriever import get_retriever


load_dotenv()


DEFAULT_MODE = os.getenv(
    "APP_MODE",
    "vulnerable",
).lower()


st.set_page_config(
    page_title="NovaAssist",
    page_icon="🔐",
    layout="wide",
)


@st.cache_resource
def load_retriever():
    return get_retriever()


def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "secure_mode" not in st.session_state:
        st.session_state.secure_mode = (
            DEFAULT_MODE == "secure"
        )


def display_sources(results):
    if not results:
        st.info(
            "No business information was retrieved."
        )
        return

    with st.expander(
        "Retrieved Business Information"
    ):
        for index, result in enumerate(
            results,
            start=1,
        ):
            st.markdown(
                f"**Source {index}:** "
                f"{result['source']}"
            )

            st.markdown(
                f"**Classification:** "
                f"`{result['classification']}`"
            )

            st.markdown(
                result["text"]
            )

            st.divider()


def main():

    initialize_session()

    st.title("NovaAssist")

    st.caption(
        "Sensitive Business Data Leakage Lab"
    )

    # =========================================================
    # Sidebar
    # =========================================================

    st.sidebar.header(
        "Lab Configuration"
    )

    secure_mode = st.sidebar.toggle(
        "Secure Mode",
        value=st.session_state.secure_mode,
    )

    if (
        secure_mode
        != st.session_state.secure_mode
    ):
        st.session_state.secure_mode = (
            secure_mode
        )

        st.session_state.messages = []

        st.rerun()

    mode = (
        "secure"
        if st.session_state.secure_mode
        else "vulnerable"
    )

    st.sidebar.markdown("---")

    user_role = st.sidebar.selectbox(
        "User Role",
        [
            "employee",
            "manager",
            "executive",
        ],
        index=0,
    )

    st.sidebar.markdown("---")

    if mode == "vulnerable":

        st.sidebar.error(
            "Application Mode: VULNERABLE"
        )

    else:

        st.sidebar.success(
            "Application Mode: SECURE"
        )

    st.sidebar.markdown(
        f"**Current Role:** `{user_role}`"
    )

    st.sidebar.markdown(
        f"**Current Mode:** `{mode}`"
    )

    # =========================================================
    # Retriever
    # =========================================================

    retriever = load_retriever()

    # =========================================================
    # Previous messages
    # =========================================================

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # =========================================================
    # User input
    # =========================================================

    query = st.chat_input(
        "Ask NovaAssist about company information..."
    )

    if not query:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    # =========================================================
    # Assistant
    # =========================================================

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching business information..."
        ):

            results = retriever.search(
                query=query,
                user_role=user_role,
                mode=mode,
            )

        display_sources(results)

        # -----------------------------------------------------
        # Build prompt
        # -----------------------------------------------------

        prompt = build_prompt(
            query=query,
            retrieved_documents=results,
        )

        # -----------------------------------------------------
        # Generate response
        # -----------------------------------------------------

        with st.spinner(
            "Generating response..."
        ):

            response = generate_response(
                prompt
            )

        # -----------------------------------------------------
        # Determine classifications
        # -----------------------------------------------------

        response_classifications = list(
            {
                result["classification"]
                for result in results
            }
        )

        # -----------------------------------------------------
        # Role-aware output guard
        # -----------------------------------------------------

        guarded_response = (
            apply_output_guard(
                text=response,
                user_role=user_role,
                response_classifications=(
                    response_classifications
                ),
                enabled=(
                    mode == "secure"
                ),
            )
        )

        st.markdown(
            guarded_response
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": guarded_response,
        }
    )


if __name__ == "__main__":
    main()