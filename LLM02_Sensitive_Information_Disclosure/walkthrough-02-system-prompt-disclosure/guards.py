"""
WT2: System Prompt & Secret Disclosure Attack & Prevention

This module contains simple security checks used in Secure Mode.
The goal is to prevent disclosure of internal prompts and application secrets.
"""

import re


# Keywords that indicate an attempt to reveal internal instructions
DISCLOSURE_PATTERNS = [
    r"system prompt",
    r"hidden prompt",
    r"hidden instruction",
    r"developer instruction",
    r"developer notes",
    r"internal prompt",
    r"show.*prompt",
    r"print.*prompt",
    r"repeat.*prompt",
    r"api key",
    r"token",
    r"secret",
    r"configuration",
    r"internal configuration",
    r"environment variable",
    r"environment",
    r"admin endpoint",
]


def is_disclosure_attempt(user_message: str) -> bool:
    """
    Returns True if the user's message appears to request
    protected internal information.
    """

    message = user_message.lower()

    return any(
        re.search(pattern, message)
        for pattern in DISCLOSURE_PATTERNS
    )


def blocked_response() -> str:
    """
    Standard response returned when a disclosure attempt is detected.
    """

    return (
        "I can't reveal internal system prompts, hidden instructions, "
        "developer notes, API keys, tokens, configuration details, "
        "or other confidential application information.\n\n"
        "If you have a legitimate software engineering question, "
        "I'd be happy to help."
    )