import joblib
from pathlib import Path
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.tree import DecisionTreeRegressor
from sklearn.pipeline import Pipeline
from prepare_data import prepare_data

def train_model():
    import pandas as pd
    from sklearn.model_selection import train_test_split, RandomizedSearchCV
    from sklearn.metrics import r2_score

    X_train, X_test, y_train, y_test, available_numeric, available_categorical = prepare_data()
    
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
    joblib.dump(best_pipeline, "model_random_forest_adresowo.pkl")
    print("✅ Model zapisano jako 'model_random_forest_adresowo.pkl'")

    return r2

if __name__ == "__main__":
    train_model()