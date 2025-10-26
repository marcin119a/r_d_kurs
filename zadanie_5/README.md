## Zadanie zaliczeniowe (projekt końcowy)

### Temat:

**Predykcja cen mieszkań w Trójmieście (Gdańsk, Gdynia, Sopot)**
— pełny pipeline: od pobrania danych po aplikację webową.

---

### Cel

Twoim zadaniem jest uruchomienie kompletnego pipeline’u opartego na kodzie z zajęć i jego rozszerzenie o analizę rynku nieruchomości w Trójmieście.
Projekt ma zademonstrować umiejętność:

* automatycznego pozyskania danych (scraping),
* ich czyszczenia, analizy i wizualizacji,
* przygotowania modelu predykcyjnego,
* wdrożenia modelu w formie aplikacji (FastAPI lub Streamlit).

---

###  Etapy projektu

#### 1. **Pobranie danych (web scraping)**

* Użyj **requests** i **BeautifulSoup** do pobrania ofert mieszkań z serwisu *adresowo.pl* lub innego źródła (Gdańsk, Gdynia, Sopot).
* Zaimplementuj pętlę pobierającą dane z kilku podstron. 
* Zapisz dane do pliku CSV (`mieszkania_trojmiasto.csv`).

Materiał referencyjny: *UOUW – Automatyzacja przetwarzania danych (skrypty)*.

---

#### 2. **Czyszczenie i przygotowanie danych**

* Wczytaj dane w Pandas.
* Usuń duplikaty i wiersze z brakami danych (`dropna()`).
* Oczyść wartości tekstowe i liczbowe (np. ceny, powierzchnie, liczby pokoi).
* Dodaj nowe kolumny, np. `price_per_m2` i `area_per_room`.
* Przefiltruj dane dla Gdańska, Gdyni i Sopotu.

Materiał referencyjny: *Analiza danych pomiarowych (Pandas)*.

---

#### 3. **Analiza i wizualizacja danych**

* Oblicz podstawowe statystyki (średnia, mediana, rozkład).
* Przedstaw dane na wykresach:

  * histogram powierzchni mieszkań,
  * boxplot cen w dzielnicach,
  * scatter plot: `area_m2` vs `price_total_zl`,
  * ranking dzielnic wg ceny za m² (bar chart lub pie chart).
* Użyj **Plotly** i zapisz wybrane wykresy do PDF przy użyciu `kaleido`.

Materiał referencyjny: *Tworzenie wykresów technicznych i raportów (Plotly)*.

---

#### 4. **Model predykcyjny**

* Przygotuj dane do modelowania:

  * one-hot encoding dla kolumn tekstowych (`locality`, `owner_direct`),
  * skalowanie (`StandardScaler`),
  * podział na zbiór treningowy i testowy.
* Wytrenuj model regresji (np. `LinearRegression` lub `RandomForestRegressor`) przewidujący cenę całkowitą.
* Zapisz model do pliku `model_trojmiasto.pkl` przy użyciu `joblib`.
* Oceń jego jakość (R², MAE, residual plot).

Materiał referencyjny: *Wprowadzenie do symulacji*.

---

#### 5. **Prototyp aplikacji webowej**

Wybierz jedną z dwóch opcji:

##### **A. FastAPI**

* Utwórz API z endpointem `/predict_price/`, który przyjmuje dane mieszkania w formacie JSON i zwraca przewidywaną cenę.
* Dodaj automatyczną dokumentację Swagger.
* Endpoint powinien korzystać z zapisanego modelu `model_trojmiasto.pkl`.

Materiał referencyjny: *UOUW – FastAPI*.

##### **B. Streamlit**

* Utwórz aplikację z prostym interfejsem do wprowadzenia danych (metraż, liczba pokoi, dzielnica, zdjęcia itp.).
* Po kliknięciu przycisku „Oblicz cenę” aplikacja wyświetla szacowaną cenę i wizualizację porównawczą.

Materiał referencyjny: *Scheduling i Streamlit*.

---

#### 6. **(Dla chętnych)** Automatyzacja

* Użyj `schedule` lub GitHub Actions do automatycznego uruchamiania scrapera raz dziennie i aktualizacji danych.

Materiał referencyjny: *Scheduling i Streamlit*.

---

### Co należy oddać:

1. Folder projektu `.zip` zawierający:

   * `scraper.py`
   * `analysis.ipynb` lub `analysis.py`
   * `model_trojmiasto.pkl`
   * `app.py` (FastAPI lub Streamlit)
   * `report.pdf` z wykresami i krótkim omówieniem wyników
2. (Opcjonalnie) link do repozytorium GitHub z projektem.

---

### Kryteria oceny:

| Kryterium                                                      | Waga |
| -------------------------------------------------------------- | ---- |
| Poprawność działania pipeline’u (scraping → model → aplikacja) | 40%  |
| Jakość kodu i czytelność (komentarze, struktura)               | 20%  |
| Jakość analizy danych i wizualizacji                           | 20%  |
| Estetyka i funkcjonalność aplikacji (FastAPI/Streamlit)        | 20%  |
