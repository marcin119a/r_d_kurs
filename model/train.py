import joblib
from pathlib import Path
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.tree import DecisionTreeRegressor
from sklearn.pipeline import Pipeline

def train_model():
    import pandas as pd
    from sklearn.model_selection import train_test_split, RandomizedSearchCV
    from sklearn.metrics import r2_score

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

    # === 5. Definicja kolumn numerycznych i kategorycznych ===
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    transformers = [("num", numeric_transformer, available_numeric)]
    if available_categorical:
        categorical_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]
        )
        transformers.append(("cat", categorical_transformer, available_categorical))

    # === 6. ColumnTransformer: preprocessing ===
    preprocessor = ColumnTransformer(transformers=transformers)

    # === 7. Pipeline z modelem ===
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                DecisionTreeRegressor(
                    max_depth=6,
                    random_state=42,
                ),
            ),
        ]
    )

    # === 8. Hiperoptymalizacja ===
    param_distributions = {
        "regressor__max_depth": [None, 4, 6, 8, 10, 15],
        "regressor__min_samples_split": [2, 5, 10, 20, 50],
        "regressor__min_samples_leaf": [1, 2, 4, 8, 12],
        "regressor__max_features": [None, "sqrt", "log2"],
    }
    search = RandomizedSearchCV(
        pipeline,
        param_distributions=param_distributions,
        n_iter=20,
        cv=5,
        scoring="r2",
        random_state=42,
        n_jobs=-1,
        refit=True,
    )
    search.fit(X_train, y_train)

    best_pipeline = search.best_estimator_
    print("🔍 Najlepsze znalezione parametry:", search.best_params_)
    print(f"📊 Najlepszy wynik walidacji krzyżowej (R²): {search.best_score_:.3f}")

    # === 9. Predykcja i ocena na zbiorze testowym ===
    y_pred = best_pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    print(f"🧪 Wynik na zbiorze testowym (R²): {r2:.3f}")

    # === 12. Zapis modelu ===
    joblib.dump(best_pipeline, "model_random_forest_adresowo_lodz.pkl")
    print("✅ Model zapisano jako 'model_random_forest_adresowo_lodz.pkl'")

    return r2

if __name__ == "__main__":
    train_model()