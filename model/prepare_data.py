from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

def prepare_data():
    # === 1. Wczytanie danych ===
    data_dir = Path(__file__).resolve().parent.parent / "scraper"
    detailed_files = sorted(data_dir.glob("*_detailed.csv"))
    if not detailed_files:
        raise FileNotFoundError(f"Nie znaleziono plików '*_detailed.csv' w katalogu {data_dir}")

    frames = []
    for csv_path in detailed_files:
        df_city = pd.read_csv(csv_path)
        parts = csv_path.stem.split("_")
        city_name = next((part for part in parts if part not in {"ogloszenia", "detailed"}), csv_path.stem)
        df_city["city"] = city_name
        df_city["source_file"] = csv_path.name
        frames.append(df_city)

    df = pd.concat(frames, ignore_index=True)

    target_column = "price_total_zl"
    if target_column not in df.columns:
        raise ValueError(f"Kolumna docelowa '{target_column}' nie została znaleziona w danych.")

    numeric_features = [
        "area",
        "rooms",
        "photo_count",
        "year_built",
        "latitude",
        "longitude",
    ]

    categorical_features = [
        "city",
        "locality",
        "street",
        "owner_type",
        "date_posted",
        "building_type",
        "floor",
        "ownership_type",
        "has_basement",
        "has_parking",
        "kitchen_type",
        "window_type",
    ]

    available_numeric = [col for col in numeric_features if col in df.columns]
    available_categorical = [col for col in categorical_features if col in df.columns]

    if not available_numeric:
        raise ValueError("Brak dostępnych kolumn numerycznych po filtracji.")

    df[target_column] = pd.to_numeric(df[target_column], errors="coerce")
    for col in available_numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=[target_column])
    df = df.dropna(subset=available_numeric, how="all")
    if "area" in df.columns:
        df = df[df["area"] > 0]
    df = df[df[target_column] > 0]
    df = df.drop_duplicates(subset=["url"], keep="last") if "url" in df.columns else df

    feature_columns = available_numeric + available_categorical

    # === 2. Definicja cech i celu ===
    X = df[feature_columns]
    y = df[target_column]

    # === 3. Podział na zbiory treningowy/testowy ===
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test, available_numeric, available_categorical
