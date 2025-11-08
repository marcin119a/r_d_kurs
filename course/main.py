import streamlit as st
import pandas as pd
import joblib

# === Funkcja predykcji ===
def predict_price(area_m2, rooms, photos, owner_direct, locality, date_posted):
   # Wczytanie modelu tylko raz (np. Random Forest z Adresowo)
   model = joblib.load("model_random_forest_adresowo_lodz.pkl")
   X_new = pd.DataFrame([[area_m2, rooms, photos, owner_direct, locality, date_posted]],
                        columns=["area_m2", "rooms", "photos", "owner_direct", "locality", "date_posted"])
   return model.predict(X_new)[0]

df = pd.read_csv("adresowo_lodz_cleaned.csv")

# === Główna logika aplikacji ===
def main():
   st.title("Predykcja ceny mieszkania (Adresowo)")
   st.write("Podaj dane mieszkania, aby uzyskać szacowaną cenę:")

   # Komponenty UI
   area = st.number_input("Powierzchnia (m²)", min_value=10.0, max_value=300.0, value=50.0)
   rooms = st.slider("Liczba pokoi", 1, 6, 3)
   photos = st.number_input("Liczba zdjęć", 0, 50, 10)
  
   owner_direct = st.checkbox("Oferta bezpośrednio od właściciela", value=True)
  
   locality = st.selectbox("Dzielnica", sorted(df['locality'].unique()))
   date_posted = st.selectbox("Data dodania ogłoszenia", sorted(df['date_posted'].unique()))

   if st.button("Oblicz cenę"):
       price = predict_price(area, rooms, photos, owner_direct, locality, date_posted)
       st.success(f"Szacowana cena: {price:,.0f} zł")

# === Punkt wejścia ===
if __name__ == "__main__":
   main()
