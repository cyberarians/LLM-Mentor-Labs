from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from guards import validate_generation_parameters, validate_prompt


BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

MODEL_PATHS = {
    "vulnerable": Path("models/vulnerable"),
    "secure": Path("models/secure"),
}

DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 80
REPEAT_COUNT = 5


def load_model(mode: str):
    model_path = MODEL_PATHS[mode]

    tokenizer = AutoTokenizer.from_pretrained(model_path)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float32,
    )

    model = PeftModel.from_pretrained(
        base_model,
        model_path,
    )

    model.eval()

    return model, tokenizer


def generate(
    model,
    tokenizer,
    prompt: str,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    prompt = validate_prompt(prompt)

    temperature, max_tokens = validate_generation_parameters(
        temperature,
        max_tokens,
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    )

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
        )

    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

    return tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    ).strip()


def prefix_completion(
    model,
    tokenizer,
    prompt: str,
) -> str:
    return generate(model, tokenizer, prompt)


def continuation_attack(
    model,
    tokenizer,
    prompt: str,
) -> str:
    return generate(model, tokenizer, prompt)


def rare_information_reconstruction(
    model,
    tokenizer,
    prompt: str,
) -> str:
    return generate(model, tokenizer, prompt)


def repeated_generation(
    model,
    tokenizer,
    prompt: str,
) -> list[str]:
    results = []

    for _ in range(REPEAT_COUNT):
        results.append(
            generate(model, tokenizer, prompt)
        )

    return results


def run_extraction_attack(
    mode: str,
    attack_type: str,
    prompt: str,
):
    model, tokenizer = load_model(mode)

    if attack_type == "Prefix Completion":
        return prefix_completion(
            model,
            tokenizer,
            prompt,
        )

    if attack_type == "Continuation Attack":
        return continuation_attack(
            model,
            tokenizer,
            prompt,
        )

    if attack_type == "Rare Information Reconstruction":
        return rare_information_reconstruction(
            model,
            tokenizer,
            prompt,
        )

    if attack_type == "Repeated Generation":
        return repeated_generation(
            model,
            tokenizer,
            prompt,
        )

    raise ValueError(
        f"Unsupported attack type: {attack_type}"
    )