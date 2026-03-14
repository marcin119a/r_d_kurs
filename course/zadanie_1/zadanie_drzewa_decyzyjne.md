## Zadanie 1 — Regresja drzewem decyzyjnym (model wieloraki)

### Cel:

Zbudować model regresji przewidujący **cenę mieszkania** na podstawie kilku zmiennych ilościowych i jednej kategorycznej, wykorzystując **drzewo decyzyjne (Decision Tree Regressor)** i **pipeline Scikit-Learn**.

---

### Kontekst:

Drzewo decyzyjne to nieliniowy model, który dzieli przestrzeń danych na mniejsze obszary w oparciu o wartości predyktorów.
W przeciwieństwie do regresji liniowej, nie zakłada ono liniowej zależności między zmiennymi a wynikiem.
Świetnie radzi sobie z danymi mieszanymi (liczbowymi i kategorycznymi) oraz pozwala łatwo interpretować wpływ cech na wynik.

---

### Instrukcja krok po kroku:

#### Wczytaj dane

Użyj danych z serwisu **adresowo.pl** (Warszawa + Wrocław):

```python
import pandas as pd
df = pd.read_csv('https://raw.githubusercontent.com/marcin119a/data/refs/heads/main/adresowo_warszawa_wroclaw.csv')
```

Usuń wiersze z brakującą ceną (`price_total_zl_cleaned`) lub powierzchnią (`area_m2`).

---

#### Wybierz zmienne objaśniające

Wybierz kilka zmiennych numerycznych, np.:

* `area_m2` — powierzchnia mieszkania,
* `rooms` — liczba pokoi,
* `photos` — liczba zdjęć w ogłoszeniu.

Dodaj również **jedną zmienną kategoryczną**, np. `locality`.

Zmienną objaśnianą (`y`) będzie **`price_total_zl_cleaned`**.

---

#### Podziel dane na zbiory treningowy i testowy

Wykorzystaj `train_test_split` z parametrem `test_size=0.2`.

---

#### Zbuduj pipeline

Użyj `ColumnTransformer` i `Pipeline`, aby:

* przeskalować zmienne numeryczne (`StandardScaler`),
* zakodować zmienne kategoryczne (`OneHotEncoder`),
* na końcu uruchomić model `DecisionTreeRegressor`.

---

#### Wytrenuj model

Dopasuj pipeline do danych treningowych (`fit`).

---

#### Oceń dopasowanie modelu

Dokonaj predykcji (`predict`) i oblicz miary dopasowania:

* **R²** – współczynnik determinacji,

---

#### Narysuj wykres residualny

Zweryfikuj, czy model nie ma systematycznych błędów:

---

---

### Zadanie do wykonania:

1. Zbuduj i wytrenuj pipeline z drzewem decyzyjnym.
2. Oblicz metryki: R².
3. Narysuj wykres reszt.
5. Dodaj zmienną `locality` (one-hot encoding) i sprawdź, **jak zmienia się R²** w porównaniu do modelu bez tej cechy.

---
