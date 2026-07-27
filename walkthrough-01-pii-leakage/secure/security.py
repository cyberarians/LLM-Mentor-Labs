import re


# --------------------------------------------------
# Sensitive Request Indicators
# --------------------------------------------------

BLOCKED_KEYWORDS = [

    # Customer Information
    "customer",
    "customers",
    "customer data",
    "customer information",
    "customer records",
    "customer profile",

    # Personally Identifiable Information (PII)
    "email",
    "emails",
    "phone",
    "phone number",
    "contact",
    "contact details",
    "cnic",
    "address",

    # Financial Information
    "balance",
    "account balance",
    "account details",
    "transaction",
    "transaction history",

    # Data Extraction
    "list",
    "show",
    "display",
    "retrieve",
    "lookup",
    "export",
    "dump",
    "database",

    # Enumeration
    "all customers",
    "all records",
    "every customer",

    # Social Engineering
    "internal audit",
    "banking audit",
    "review customer accounts",

    # Profile Requests
    "identify customer",
    "complete profile"
]


# --------------------------------------------------
# Authorization
# --------------------------------------------------

def is_authorized():
    """
    Simulates user authorization.

    Walkthrough 1 assumes every user is unauthorized.
    """

    return False


# --------------------------------------------------
# Detect Sensitive Requests
# --------------------------------------------------

def contains_sensitive_request(user_query):
    """
    Detects whether the user is requesting
    sensitive customer information.
    """

    query = user_query.lower()

    return any(keyword in query for keyword in BLOCKED_KEYWORDS)


# --------------------------------------------------
# Request Validation
# --------------------------------------------------

def validate_request(user_query):
    """
    Prevent unauthorized requests before
    they reach the LLM.
    """

    if contains_sensitive_request(user_query):

        if not is_authorized():

            return (
                False,
                "Access Denied: You are not authorized to access customer information."
            )

    return True, None


# --------------------------------------------------
# Data Minimization
# --------------------------------------------------

def prepare_customer_data(customer_data, user_query):
    """
    Apply the principle of least privilege.

    Unauthorized users never receive
    customer records.
    """

    if contains_sensitive_request(user_query):
        return []

    return customer_data


# --------------------------------------------------
# Output Filtering
# --------------------------------------------------

def mask_pii(response):
    """
    Redact sensitive information that
    may appear in the LLM response.
    """

    # Customer IDs
    response = re.sub(
        r"CUST-\d+",
        "[REDACTED CUSTOMER ID]",
        response
    )

    # CNIC
    response = re.sub(
        r"\b\d{5}-\d{7}-\d\b",
        "*****-*******-*",
        response
    )

    # Phone Number
    response = re.sub(
        r"\+92-\d{3}-\d{7}",
        "+92-XXX-XXXXXXX",
        response
    )

    # Email
    response = re.sub(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        "[REDACTED EMAIL]",
        response
    )

    # Account Balance
    response = re.sub(
        r"PKR\s[\d,]+",
        "[REDACTED BALANCE]",
        response
    )

    return response