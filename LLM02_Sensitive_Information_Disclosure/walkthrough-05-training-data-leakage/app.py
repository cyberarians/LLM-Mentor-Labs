import streamlit as st

from extraction import run_extraction_attack
from guards import validate_request


st.set_page_config(
    page_title="Training Data Leakage Lab",
    page_icon="🔐",
)

st.title("Training Data Leakage & Memorization Attack")

st.write(
    "Test whether sensitive information included in training data "
    "can be reproduced by the model."
)

st.divider()

mode = st.toggle(
    "Secure Mode",
    value=False,
)

selected_mode = "secure" if mode else "vulnerable"

if selected_mode == "secure":
    st.success("Secure Model")
else:
    st.error("Vulnerable Model")

attack_type = st.selectbox(
    "Attack Type",
    [
        "Prefix Completion",
        "Continuation Attack",
        "Rare Information Reconstruction",
        "Repeated Generation",
    ],
)

prompt = st.text_area(
    "Attack Prompt",
    height=120,
    placeholder="Enter your attack prompt...",
)

if st.button("Run Attack", type="primary"):

    try:
        selected_mode, attack_type, prompt = validate_request(
            selected_mode,
            attack_type,
            prompt,
        )

        with st.spinner("Generating response..."):
            result = run_extraction_attack(
                selected_mode,
                attack_type,
                prompt,
            )

        st.subheader("Model Output")

        st.markdown(
            """
            <style>
            .chat-output {
                width: 100%;
                padding: 16px;
                border: 1px solid #444;
                border-radius: 10px;
                white-space: pre-wrap;
                overflow-wrap: anywhere;
                word-break: break-word;
                line-height: 1.5;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        if isinstance(result, list):
            for index, output in enumerate(result, start=1):
                st.markdown(f"**Generation {index}**")

                st.markdown(
                    f'<div class="chat-output">{output}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                f'<div class="chat-output">{result}</div>',
                unsafe_allow_html=True,
            )

    except (ValueError, TypeError) as error:
        st.warning(str(error))