import re


ROLE_ACCESS = {
    "employee": {
        "public",
    },
    "manager": {
        "public",
        "internal",
    },
    "executive": {
        "public",
        "internal",
        "confidential",
    },
}


SENSITIVE_PATTERNS = [
    r"\$\s?\d+(?:[.,]\d+)?\s?(?:million|billion|thousand)?",
    r"\b\d+(?:[.,]\d+)?\s?(?:million|billion|thousand)\s?(?:dollars|USD)?\b",

    r"\b(?:total\s+)?revenue\b",
    r"\b(?:quarterly|annual|yearly|q[1-4])\s+revenue\b",
    r"\bsales\s+(?:figures|data|performance|results)\b",

    r"\b(?:enterprise\s+)?pricing\b",
    r"\bpricing\s+(?:strategy|plan|model|policy)\b",
    r"\b(?:approved|max(?:imum)?|negotiated)\s+discount\b",
    r"\bdiscount\s+(?:range|limit|policy)\b",
    r"\b\d+(?:\.\d+)?%\s*(?:discount|off)\b",

    r"\bproject\s+orion\b",
    r"\bproject\s+atlas\b",
    r"\bproduct\s+roadmap\b",
    r"\bupcoming\s+product\b",
    r"\bunreleased\s+(?:product|feature|features)\b",
    r"\btarget\s+launch\b",
    r"\blaunch\s+(?:date|schedule|strategy)\b",

    r"\bpotential\s+acquisition\b",
    r"\bplanned\s+acquisition\b",
    r"\bproposed\s+acquisition\b",
    r"\bacquisition\s+(?:plan|strategy|evaluation)\b",
    r"\bmerger\s+(?:plan|strategy|evaluation)\b",
    r"\bdue\s+diligence\b",

    r"\binternal\s+strategy\b",
    r"\bstrategic\s+(?:initiative|initiatives|plan|plans)\b",
    r"\bstrategic\s+(?:opportunity|opportunities)\b",
    r"\bexecutive\s+(?:decision|decisions|meeting|meetings)\b",
    r"\bconfidential\s+(?:meeting|decision|information)\b",

    r"\bhighly\s+confidential\b",
    r"\bconfidential\s+(?:information|business)\b",
    r"\binternal\s+only\b",
    r"\bnot\s+(?:publicly\s+)?announced\b",
]


def get_allowed_classifications(role):
    return ROLE_ACCESS.get(
        role,
        {"public"},
    )


def contains_sensitive_information(text):
    for pattern in SENSITIVE_PATTERNS:
        if re.search(
            pattern,
            text,
            re.IGNORECASE,
        ):
            return True

    return False


def redact_sensitive_information(text):
    redacted_text = text

    for pattern in SENSITIVE_PATTERNS:
        redacted_text = re.sub(
            pattern,
            "[REDACTED]",
            redacted_text,
            flags=re.IGNORECASE,
        )

    return redacted_text


def apply_output_guard(
    text,
    user_role,
    response_classifications,
    enabled=True,
):
    if not enabled:
        return text

    allowed_classifications = get_allowed_classifications(
        user_role
    )

    unauthorized_classifications = set(
        response_classifications
    ) - allowed_classifications

    if unauthorized_classifications:
        return redact_sensitive_information(text)

    return text