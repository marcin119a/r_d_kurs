
## Zadanie 2 — Udostępnienie modelu przez API (FastAPI)

### Cel:

Utworzyć prosty serwer API z FastAPI, który wczyta wytrenowany model (z pliku `.pkl` lub `.joblib`) i umożliwi przewidywanie ceny mieszkania na podstawie danych wejściowych przesłanych w żądaniu POST.

---

### Kontekst:

Masz już wytrenowany model (np. `best_random_forest_model.pkl`) .
Teraz chcesz, aby inni mogli z niego korzystać przez API — np. wysyłając dane o mieszkaniu w formacie JSON i otrzymując prognozowaną cenę.

---

### Instrukcja krok po kroku

#### Utwórz plik `app.py`

1. Przygotuj odpowiedni entpoint.

---

#### Uruchom serwer lokalnie 

Serwer wystartuje na adresie:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

#### Przetestuj endpoint

Otwórz w przeglądarce:
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Następnie wybierz endpoint:
`POST /predict_price/`
i wprowadź dane testowe, np.:

```json
{
  "area_m2": 47,
  "locality": "Warszawa Ochota",
  "rooms": 2,
  "owner_direct": true,
  "photos": 16,
  "date_posted": "6 dni temu"
}
```

Po kliknięciu **Execute** otrzymasz wynik:

```json
{
  "predicted_price": <jakaś wartość>
}
```

---

#### Zadanie do wykonania

1. Wczytaj wytrenowany model (np. z Zadania 1).
2. Utwórz endpoint `POST /predict_price/`, który przyjmuje dane mieszkania i zwraca prognozę.
3. (Opcjonalnie) dodaj endpoint `/train_model/`, który ponownie trenuje model i zapisuje go do pliku.
4. Przetestuj API w interfejsie Swagger (`/docs`).

---
