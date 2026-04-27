import os
import torch
import pandas as pd
from datasets import Dataset
from transformers import (
    AutoModelForMaskedLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments
)

def train_domain_adaptation():
    """
    Skrypt do Continued Pre-training (MLM) na danych nieruchomości.
    Uczy model specyficznego żargonu i reprezentacji ofert.
    """
    print("=== Rozpoczynam przygotowanie do treningu MLM (Domain Adaptation) ===")

    # 1. Konfiguracja
    model_name = "allegro/herbert-base-cased"
    input_file = "data/ogloszenia_polska_unified.parquet"
    output_dir = "./herbert-nieruchomosci-pl"
    
    if not os.path.exists(input_file):
        print(f"Błąd: Nie znaleziono pliku {input_file}. Uruchom najpierw create_unified_dataset.py")
        return

    # 2. Wczytanie danych
    print(f"Wczytywanie danych z {input_file}...")
    df = pd.read_parquet(input_file)
    
    # Przygotowanie tekstu: łączymy miasto, dzielnicę i opis dla pełnego kontekstu
    # Usuwamy puste opisy
    df = df.dropna(subset=['description_text'])
    
    def prepare_text(row):
        return f"Miasto: {row['source_city']}. Lokalizacja: {row['locality']}. Opis: {row['description_text']}"

    df['text_for_mlm'] = df.apply(prepare_text, axis=1)
    dataset = Dataset.from_pandas(df[['text_for_mlm']])

    # 3. Tokenizacja
    print(f"Inicjalizacja modelu i tokenizera: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name)

    def tokenize_function(examples):
        return tokenizer(
            examples["text_for_mlm"],
            truncation=True,
            padding="max_length",
            max_length=512
        )

    print("Tokenizacja zbioru danych...")
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        num_proc=4,
        remove_columns=["text_for_mlm"]
    )

    # 4. Data Collator dla MLM (maskowanie 15% tokenów)
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, 
        mlm=True, 
        mlm_probability=0.15
    )

    # 5. Argumenty treningu
    # Jeśli masz GPU (CUDA/MPS), skrypt automatycznie go użyje
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Używane urządzenie: {device}")

    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=3,              # Na początek 3 epoki wystarczą
        per_device_train_batch_size=4,   # Mały batch, aby uniknąć błędów pamięci (OOM)
        save_steps=500,
        save_total_limit=2,
        prediction_loss_only=True,
        logging_steps=100,
        learning_rate=5e-5,
        weight_decay=0.01,
        push_to_hub=False,               # Możesz zmienić na True, aby wysłać model na HF
    )

    # 6. Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=tokenized_dataset,
    )

    # 7. Trening
    print("\nRozpoczynam trening. To może potrwać od kilku minut do kilku godzin zależnie od Twojego sprzętu...")
    trainer.train()

    # 8. Zapisanie modelu
    print(f"\nTrening zakończony. Zapisuję model w {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Gotowe!")

if __name__ == "__main__":
    train_domain_adaptation()
