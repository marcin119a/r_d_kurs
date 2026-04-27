from transformers import AutoModelForMaskedLM, AutoTokenizer
from huggingface_hub import HfApi

MODEL_DIR = "./herbert-nieruchomosci-pl"
REPO_ID = "marcin119a/herbert-nieruchomosci-pl"
DATASET_REPO_ID = "marcin119a/nieruchomosci-polska-mlm"
BASE_MODEL = "allegro/herbert-base-cased"

MODEL_CARD = f"""---
language:
- pl
license: mit
base_model: {BASE_MODEL}
datasets:
- {DATASET_REPO_ID}
tags:
- fill-mask
- masked-language-modeling
- real-estate
- polish
- domain-adaptation
---

# Herbert — Nieruchomości PL (MLM)

Model [`{BASE_MODEL}`](https://huggingface.co/{BASE_MODEL}) poddany domain adaptation
na polskich ogłoszeniach nieruchomości metodą Masked Language Modeling (MLM).

## Dane treningowe

Dataset: [{DATASET_REPO_ID}](https://huggingface.co/datasets/{DATASET_REPO_ID})

Ogłoszenia nieruchomości z różnych miast Polski zawierające opisy mieszkań, domów i działek.

## Trening

- **Metoda:** Masked Language Modeling (15% maskowań)
- **Epoki:** 3
- **Optymalizator:** AdamW, lr=2e-5, weight_decay=0.01
- **Scheduler:** cosine z warmup 5%

## Użycie

```python
from transformers import pipeline

pipe = pipeline("fill-mask", model="{REPO_ID}")
results = pipe("Mieszkanie na sprzedaż w centrum [MASK].")
for r in results:
    print(r["token_str"], r["score"])
```
"""


def main():
    api = HfApi()
    user = api.whoami()["name"]
    print(f"Zalogowany jako: {user}")

    print(f"Ładowanie modelu z {MODEL_DIR}...")
    model = AutoModelForMaskedLM.from_pretrained(MODEL_DIR)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

    print(f"Tworzenie repozytorium: {REPO_ID}")
    api.create_repo(repo_id=REPO_ID, repo_type="model", exist_ok=True)

    print("Wysyłanie modelu...")
    model.push_to_hub(REPO_ID)

    print("Wysyłanie tokenizera...")
    tokenizer.push_to_hub(REPO_ID)

    print("Zapisywanie model card...")
    api.upload_file(
        path_or_fileobj=MODEL_CARD.encode(),
        path_in_repo="README.md",
        repo_id=REPO_ID,
        repo_type="model",
    )

    print(f"\nSUKCES! Model dostępny pod:")
    print(f"  https://huggingface.co/{REPO_ID}")
    print(f"\nJak użyć:")
    print(f"  from transformers import pipeline")
    print(f"  pipe = pipeline('fill-mask', model='{REPO_ID}')")


if __name__ == "__main__":
    main()
