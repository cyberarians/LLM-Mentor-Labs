import os
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)


BASE_MODEL = os.getenv(
    "BASE_MODEL",
    "Qwen/Qwen2.5-0.5B-Instruct",
)

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", "models"))

MAX_LENGTH = int(os.getenv("MAX_LENGTH", "256"))

LORA_CONFIG = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],
)


def load_base_model():
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float32,
    )

    model = get_peft_model(model, LORA_CONFIG)

    return model, tokenizer


def prepare_dataset(path: Path, tokenizer):
    dataset = load_dataset(
        "json",
        data_files=str(path),
        split="train",
    )

    def tokenize(example):
        return tokenizer(
            example["text"],
            truncation=True,
            max_length=MAX_LENGTH,
        )

    return dataset.map(
        tokenize,
        remove_columns=dataset.column_names,
    )


def train_model(
    data_path: Path,
    output_dir: Path,
):
    output_dir.mkdir(parents=True, exist_ok=True)

    model, tokenizer = load_base_model()
    dataset = prepare_dataset(data_path, tokenizer)

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=5,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        learning_rate=2e-4,
        logging_steps=1,
        save_strategy="no",
        report_to="none",
        use_cpu=True,
        fp16=False,
        bf16=False,
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
    )

    trainer.train()

    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    return output_dir


def train_vulnerable():
    return train_model(
        DATA_DIR / "training" / "sensitive_training_data.jsonl",
        MODEL_DIR / "vulnerable",
    )


def train_secure():
    return train_model(
        DATA_DIR / "sanitized" / "sanitized_training_data.jsonl",
        MODEL_DIR / "secure",
    )


def main():
    train_vulnerable()
    train_secure()


if __name__ == "__main__":
    main()