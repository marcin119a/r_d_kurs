import torch
from datasets import load_dataset
from transformers import (
    AutoModelForMaskedLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

REPO_ID = "marcin119a/nieruchomosci-polska-mlm"
MODEL_NAME = "allegro/herbert-base-cased"
OUTPUT_DIR = "./herbert-nieruchomosci-pl"
MAX_LENGTH = 512


def train_domain_adaptation():
    print("=== MLM Domain Adaptation — Herbert na danych nieruchomości ===")

    device = (
        "cuda"
        if torch.cuda.is_available()
        else ("mps" if torch.backends.mps.is_available() else "cpu")
    )
    print(f"Urządzenie: {device}")
    use_fp16 = device == "cuda"

    print(f"Ładowanie datasetu z HuggingFace: {REPO_ID}")
    dataset = load_dataset(REPO_ID)
    print(f"Train: {len(dataset['train'])}, Validation: {len(dataset['validation'])}")

    print(f"Inicjalizacja tokenizera i modelu: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME)

    if device == "cuda":
        model.gradient_checkpointing_enable()

    def tokenize(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
        )

    print("Tokenizacja...")
    tokenized = dataset.map(
        tokenize,
        batched=True,
        num_proc=4,
        remove_columns=["text"],
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=True,
        mlm_probability=0.15,
    )

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=8 if device == "cuda" else 4,
        per_device_eval_batch_size=8 if device == "cuda" else 4,
        gradient_accumulation_steps=2,
        learning_rate=2e-5,
        weight_decay=0.01,
        warmup_ratio=0.05,
        lr_scheduler_type="cosine",
        fp16=use_fp16,
        eval_strategy="steps",
        eval_steps=500,
        save_strategy="steps",
        save_steps=500,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        logging_steps=100,
        report_to="none",
        push_to_hub=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
    )

    print("\nRozpoczynam trening...")
    trainer.train()

    print(f"\nTrening zakończony. Zapisuję model w {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Gotowe!")


if __name__ == "__main__":
    train_domain_adaptation()
