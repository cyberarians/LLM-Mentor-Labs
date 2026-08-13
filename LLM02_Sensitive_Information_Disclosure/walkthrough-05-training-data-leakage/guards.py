from typing import Any


ALLOWED_MODES = {"vulnerable", "secure"}

ALLOWED_ATTACKS = {
    "Prefix Completion",
    "Continuation Attack",
    "Rare Information Reconstruction",
    "Repeated Generation",
}

MAX_PROMPT_LENGTH = 2000


def validate_prompt(prompt: Any) -> str:
    """Validate and normalize a user-provided prompt."""

    if not isinstance(prompt, str):
        raise TypeError("Prompt must be a string.")

    prompt = prompt.strip()

    if not prompt:
        raise ValueError("Prompt cannot be empty.")

    if len(prompt) > MAX_PROMPT_LENGTH:
        raise ValueError(
            f"Prompt must not exceed {MAX_PROMPT_LENGTH} characters."
        )

    return prompt


def validate_mode(mode: Any) -> str:
    """Validate the selected model mode."""

    if not isinstance(mode, str):
        raise TypeError("Model mode must be a string.")

    mode = mode.strip().lower()

    if mode not in ALLOWED_MODES:
        raise ValueError(
            f"Invalid model mode. Choose one of: "
            f"{', '.join(sorted(ALLOWED_MODES))}."
        )

    return mode


def validate_attack_type(attack_type: Any) -> str:
    """Validate the selected extraction attack."""

    if not isinstance(attack_type, str):
        raise TypeError("Attack type must be a string.")

    attack_type = attack_type.strip()

    if attack_type not in ALLOWED_ATTACKS:
        raise ValueError(
            f"Unsupported attack type: {attack_type}"
        )

    return attack_type


def validate_generation_parameters(
    temperature: float,
    max_tokens: int,
) -> tuple[float, int]:
    """Validate model generation parameters."""

    if not 0.0 <= temperature <= 2.0:
        raise ValueError("Temperature must be between 0.0 and 2.0.")

    if not 1 <= max_tokens <= 512:
        raise ValueError("max_tokens must be between 1 and 512.")

    return temperature, max_tokens


def validate_request(
    mode: Any,
    attack_type: Any,
    prompt: Any,
) -> tuple[str, str, str]:
    """Validate a complete extraction request."""

    mode = validate_mode(mode)
    attack_type = validate_attack_type(attack_type)
    prompt = validate_prompt(prompt)

    return mode, attack_type, prompt