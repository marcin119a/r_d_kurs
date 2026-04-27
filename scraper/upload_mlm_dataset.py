import pandas as pd
from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi

REPO_ID = "marcin119a/nieruchomosci-polska-mlm"
INPUT_FILE = "data/ogloszenia_polska_unified.parquet"
TEST_SIZE = 0.05

def prepare_text(row):
    parts = [f"Miasto: {row['source_city']}"]
    if pd.notna(row.get('locality')) and row['locality']:
        parts.append(f"Lokalizacja: {row['locality']}")
    if pd.notna(row.get('description_text')) and row['description_text']:
        parts.append(f"Opis: {row['description_text']}")
    return ". ".join(parts)

def main():
    print(f"Wczytywanie danych z {INPUT_FILE}...")
    df = pd.read_parquet(INPUT_FILE)
    df = df.dropna(subset=['description_text'])
    df = df[df['description_text'].str.strip() != '']

    print(f"Rekordów po filtracji: {len(df)}")
    print("Rozkład miast:")
    print(df['source_city'].value_counts().to_string())

    df['text'] = df.apply(prepare_text, axis=1)

    dataset = Dataset.from_pandas(df[['text']], preserve_index=False)
    split = dataset.train_test_split(test_size=TEST_SIZE, seed=42)
    dataset_dict = DatasetDict({"train": split["train"], "validation": split["test"]})

    print(f"\nPodział: train={len(dataset_dict['train'])}, validation={len(dataset_dict['validation'])}")

    api = HfApi()
    user = api.whoami()['name']
    print(f"\nZalogowany jako: {user}")
    print(f"Wysyłanie do: {REPO_ID}")

    dataset_dict.push_to_hub(REPO_ID, private=False)

    print(f"\nSUKCES! Dataset dostępny pod:")
    print(f"  https://huggingface.co/datasets/{REPO_ID}")
    print(f"\nJak załadować:")
    print(f"  from datasets import load_dataset")
    print(f"  ds = load_dataset('{REPO_ID}')")

if __name__ == "__main__":
    main()
