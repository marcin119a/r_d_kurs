import pandas as pd
import glob
import os

def create_unified_dataset():
    """
    Łączy wszystkie wyczyszczone pliki miast w jeden spójny zbiór danych.
    Zapisuje wynik w formacie CSV i Parquet (lepszy dla dużych zbiorów danych).
    """
    print("=== Tworzenie zunifikowanego zbioru danych ===")
    
    # Znajdź wszystkie wyczyszczone pliki (nowa struktura podfolderów)
    files = glob.glob("data/scraped-data-*/*_cleaned.csv")
    if not files:
        files = glob.glob("data/*_cleaned.csv")
    
    if not files:
        print("Nie znaleziono plików *_cleaned.csv w folderze data/.")
        return

    all_dfs = []
    for f in files:
        filename = os.path.basename(f)
        city = filename.replace("ogloszenia_", "").replace("_cleaned.csv", "")
        
        print(f"Dodaję miasto: {city}...")
        df = pd.read_csv(f)
        df['source_city'] = city
        all_dfs.append(df)
    
    # Łączenie
    unified_df = pd.concat(all_dfs, ignore_index=True)
    
    # Czyszczenie typów dla formatu Parquet (kolumny z mieszanymi typami)
    # photo_count często zawiera napisy typu "+3 podobne oferty"
    if 'photo_count' in unified_df.columns:
        unified_df['photo_count'] = unified_df['photo_count'].astype(str)
    
    # Statystyki
    print(f"\nŁączna liczba ogłoszeń: {len(unified_df)}")
    print("Rozkład miast:")
    print(unified_df['source_city'].value_counts())
    
    # Zapisywanie
    output_csv = "data/ogloszenia_polska_unified.csv"
    output_parquet = "data/ogloszenia_polska_unified.parquet"
    
    print(f"\nZapisywanie do CSV: {output_csv}")
    unified_df.to_csv(output_csv, index=False)
    
    print(f"Zapisywanie do Parquet: {output_parquet}")
    unified_df.to_parquet(output_parquet, index=False)
    
    print("\nGotowe! Plik Parquet jest optymalny do pracy z Hugging Face i biblioteką datasets.")

if __name__ == "__main__":
    create_unified_dataset()
