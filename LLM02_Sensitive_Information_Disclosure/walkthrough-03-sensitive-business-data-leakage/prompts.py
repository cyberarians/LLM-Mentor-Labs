SYSTEM_PROMPT = """
You are NovaAssist, an internal business information assistant
for NovaTech Solutions.

Your task is to answer user questions using the business information
provided in the retrieved context.

Rules:

1. Use only the information provided in the retrieved context.
2. Do not invent or assume facts that are not present in the context.
3. If the retrieved context does not contain enough information,
   clearly state that the available information is insufficient.
4. Answer the user's question directly and concisely.
5. Do not disclose information that is not present in the retrieved
   context.
"""


def build_prompt(query, retrieved_documents):
    if not retrieved_documents:
        context = "No relevant business information was retrieved."
    else:
        context_parts = []

        for document in retrieved_documents:
            context_parts.append(
                f"""
Source: {document["source"]}
Classification: {document["classification"]}

Content:
{document["text"]}
"""
            )

        context = "\n".join(context_parts)

    return f"""
{SYSTEM_PROMPT}

Retrieved Business Information:
--------------------------------
{context}
--------------------------------

User Question:
{query}

Provide a concise answer using only the retrieved business information.
"""