"""
Ewaluacja jakości modelu Herbert dostrojonego na danych nieruchomości.
Porównuje oryginalny Herbert vs fine-tuned na 3 metrykach:
  1. Eval loss / perplexity na zbiorze walidacyjnym
  2. Fill-mask — jakościowe testy zdań branżowych
"""

import math
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForMaskedLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
    pipeline,
)

FINETUNED_DIR = "./herbert-nieruchomosci-pl"
BASE_MODEL = "allegro/herbert-base-cased"
REPO_ID = "marcin119a/nieruchomosci-polska-mlm"
MAX_LENGTH = 512
EVAL_SAMPLES = 500  # ogranicz żeby było szybko; None = cały zbiór


FILL_MASK_SENTENCES = [
    "Mieszkanie do wynajęcia w centrum <mask>, 3 pokoje, balkon.",
    "Cena za metr kwadratowy wynosi <mask> złotych.",
    "Nieruchomość posiada <mask> i ogrzewanie miejskie.",
    "Apartament na <mask> piętrze z windą i miejscem parkingowym.",
    "Do <mask> wliczone są media: prąd, woda, internet.",
]


def compute_perplexity(model_path_or_name: str, eval_dataset, tokenizer) -> dict:
    print(f"\n  Ładowanie modelu: {model_path_or_name}")
    model = AutoModelForMaskedLM.from_pretrained(model_path_or_name)

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=True, mlm_probability=0.15
    )

    args = TrainingArguments(
        output_dir="/tmp/eval_tmp",
        per_device_eval_batch_size=16,
        report_to="none",
        use_cpu=not torch.cuda.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=args,
        data_collator=data_collator,
        eval_dataset=eval_dataset,
    )

    metrics = trainer.evaluate()
    loss = metrics["eval_loss"]
    perplexity = math.exp(loss)
    return {"loss": loss, "perplexity": perplexity}


def fill_mask_comparison(sentences: list[str]):
    print("\n" + "=" * 60)
    print("FILL-MASK: porównanie predykcji")
    print("=" * 60)

    models = {
        "Herbert bazowy": BASE_MODEL,
        "Fine-tuned (nieruchomości)": FINETUNED_DIR,
    }

    for sentence in sentences:
        print(f"\nZdanie: {sentence}")
        for label, path in models.items():
            pipe = pipeline("fill-mask", model=path, tokenizer=path, top_k=5)
            results = pipe(sentence)
            tokens = [f"{r['token_str']} ({r['score']:.2%})" for r in results]
            print(f"  [{label}]: {' | '.join(tokens)}")


def main():
    print("=== Ewaluacja MLM: Herbert vs Herbert-nieruchomości ===\n")

    print("Ładowanie datasetu z HuggingFace...")
    dataset = load_dataset(REPO_ID)
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    def tokenize(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
        )

    val_data = dataset["validation"]
    if EVAL_SAMPLES:
        val_data = val_data.select(range(min(EVAL_SAMPLES, len(val_data))))
    print(f"Zbiór walidacyjny: {len(val_data)} przykładów")

    tokenized_val = val_data.map(
        tokenize, batched=True, num_proc=2, remove_columns=["text"]
    )

    # --- Perplexity ---
    print("\n" + "=" * 60)
    print("PERPLEXITY na zbiorze walidacyjnym")
    print("=" * 60)

    results = {}
    for label, path in [
        ("Herbert bazowy", BASE_MODEL),
        ("Fine-tuned (nieruchomości)", FINETUNED_DIR),
    ]:
        print(f"\n[{label}]")
        m = compute_perplexity(path, tokenized_val, tokenizer)
        results[label] = m
        print(f"  Loss:        {m['loss']:.4f}")
        print(f"  Perplexity:  {m['perplexity']:.2f}")

    print("\n" + "=" * 60)
    print("PODSUMOWANIE")
    print("=" * 60)
    base = results["Herbert bazowy"]
    ft = results["Fine-tuned (nieruchomości)"]
    delta_ppl = base["perplexity"] - ft["perplexity"]
    print(f"  Bazowy perplexity:    {base['perplexity']:.2f}")
    print(f"  Fine-tuned perplexity:{ft['perplexity']:.2f}")
    if delta_ppl > 0:
        print(f"  Poprawa: -{delta_ppl:.2f} pkt perplexity (fine-tuned jest lepszy)")
    else:
        print(f"  Pogorszenie: +{abs(delta_ppl):.2f} pkt (sprawdź trening)")

    # --- Fill-mask ---
    fill_mask_comparison(FILL_MASK_SENTENCES)


if __name__ == "__main__":
    main()
