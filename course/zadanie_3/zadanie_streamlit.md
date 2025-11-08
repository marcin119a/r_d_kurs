

## **Zadanie: Aplikacja Streamlit do predykcji ceny mieszkania**

### **Cel:**

Zbuduj aplikację webową w **Streamlit**, która:

* wczytuje zapisany model `best_random_forest_model.pkl`,
* umożliwia użytkownikowi wprowadzenie danych mieszkania,
* wyświetla prognozowaną cenę.

---

### **Struktura projektu**

```
projekt_streamlit/
├── best_random_forest_model.pkl
├── app.py
└── requirements.txt
```

---

### **Krok 1 — Przygotowanie środowiska**

W terminalu:

```bash
pip install streamlit joblib pandas scikit-learn
```

---

### **Krok 2 — Utwórz plik `main.py`**


---

### **Krok 3 — Uruchom aplikację**

W terminalu:

```bash
streamlit run main.py
```

Aplikacja otworzy się w przeglądarce pod adresem:
👉 [http://localhost:8501](http://localhost:8501)

---

### **Krok 4 — Rozszerzenia (dla chętnych)**

1. Dodaj wykres słupkowy z porównaniem:

   * przewidywanej ceny,
   * średniej ceny rynkowej dla danej lokalizacji.

2. Zastosuj formatowanie danych:

   ```python
   st.metric("Szacowana cena", f"{predicted_price:,.0f} zł")
   ```

3. Dodaj możliwość **załadowania danych z CSV**:

   ```python
   uploaded_file = st.file_uploader("Wczytaj plik CSV", type="csv")
   ```

---

### **Zadanie do wykonania**

1. Wczytaj model `best_random_forest_model.pkl`.
2. Zbuduj prosty interfejs z komponentami:

   * `st.number_input`, `st.selectbox`, `st.checkbox`, `st.slider`
3. Przygotuj dane wejściowe w `DataFrame` (dokładnie takie kolumny, jak w treningu).
4. Oblicz i wyświetl cenę mieszkania.
5. (Dla chętnych) Dodaj wykres lub porównanie z medianą ceny.

---

### **Pytania do dyskusji**

* Jak zapewnić, by aplikacja zawsze używała aktualnej wersji modelu?
* Jakie problemy mogą wystąpić, jeśli model nie był zapisany jako pełny pipeline?
* Jak można wdrożyć tę aplikację np. na **Streamlit Cloud** lub **Render**?

