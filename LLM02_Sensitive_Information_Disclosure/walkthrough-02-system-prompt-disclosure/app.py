import streamlit as st

from guards import blocked_response, is_disclosure_attempt
from llm import generate_response


# ----------------------------------------------------------
# Page Configuration
# ----------------------------------------------------------

st.set_page_config(
    page_title="LLMentor | WT2",
    page_icon="🔐",
    layout="wide",
)

# ----------------------------------------------------------
# Header
# ----------------------------------------------------------

st.title("🔐 LLMentor Security Labs")
st.subheader("Walkthrough 2: System Prompt & Secret Disclosure Attack & Prevention")

st.divider()

# ----------------------------------------------------------
# Protection Mode
# ----------------------------------------------------------

st.markdown("### 🛡️ Protection Mode")

mode = st.radio(
    label="",
    options=["Vulnerable", "Secure"],
    horizontal=True,
)

if mode == "Vulnerable":
    st.error("🔴 Vulnerable Mode Enabled")
else:
    st.success("🟢 Secure Mode Enabled")

st.divider()

# ----------------------------------------------------------
# Chat Section
# ----------------------------------------------------------

st.markdown("## 💬 DevAssist AI")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I'm **DevAssist AI**.\n\n"
                "I can help with software engineering, debugging, "
                "and programming questions."
            ),
        }
    ]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------------------------------------------------
# User Input
# ----------------------------------------------------------

prompt = st.chat_input("Ask DevAssist AI...")

if prompt:

    # Show user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    if mode == "Secure" and is_disclosure_attempt(prompt):
        response = blocked_response()
    else:
        response = generate_response(
            user_message=prompt,
            mode=mode,
        )

    # Show assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(response)