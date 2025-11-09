import pandas as pd
import argparse
import os

def clean_scraped_data(input_file, output_file=None, min_valid_fields=5, remove_price_ask=False):
    """
    Czyści dane zeskrapowane z adresowo.pl.
    
    Args:
        input_file (str): Ścieżka do pliku CSV z surowymi danymi
        output_file (str): Ścieżka do pliku wyjściowego (domyślnie: {input}_cleaned.csv)
        min_valid_fields (int): Minimalna liczba niepustych pól wymagana do zachowania wiersza
        remove_price_ask (bool): Czy usuwać wiersze z "zapytaj o cenę"
    """
    print(f"Wczytuję dane z: {input_file}")
    
    # Wczytaj dane
    df = pd.read_csv(input_file)
    initial_count = len(df)
    print(f"Początkowa liczba wierszy: {initial_count}")
    
    # Statystyki przed czyszczeniem
    print("\nStatystyki przed czyszczeniem:")
    print(f"  - Całkowicie puste wiersze: {df.isna().all(axis=1).sum()}")
    print(f"  - Wiersze z NaN w locality: {df['locality'].isna().sum()}")
    print(f"  - Wiersze z NaN w street: {df['street'].isna().sum()}")
    print(f"  - Wiersze z NaN w rooms: {df['rooms'].isna().sum()}")
    print(f"  - Wiersze z NaN w area: {df['area'].isna().sum()}")
    print(f"  - Wiersze z NaN w price_total_zl: {df['price_total_zl'].isna().sum()}")
    
    # Policz ile niepustych wartości ma każdy wiersz
    non_na_count = df.notna().sum(axis=1)
    
    # Usuń wiersze z małą liczbą niepustych pól
    df_cleaned = df[non_na_count >= min_valid_fields].copy()
    removed_sparse = initial_count - len(df_cleaned)
    print(f"\nUsunięto {removed_sparse} wierszy z mniej niż {min_valid_fields} niepustych pól")
    
    # Usuń wiersze bez podstawowych informacji (locality i street)
    df_cleaned = df_cleaned.dropna(subset=['locality', 'street'])
    removed_no_location = len(df) - removed_sparse - len(df_cleaned)
    if removed_no_location > 0:
        print(f"Usunięto {removed_no_location} wierszy bez lokalizacji (locality/street)")
    
    # Opcjonalnie usuń wiersze z "zapytaj o cenę"
    if remove_price_ask:
        before_price_filter = len(df_cleaned)
        df_cleaned = df_cleaned[
            ~df_cleaned['price_total_zl'].astype(str).str.contains('zapytaj', case=False, na=False)
        ]
        removed_ask_price = before_price_filter - len(df_cleaned)
        if removed_ask_price > 0:
            print(f"Usunięto {removed_ask_price} wierszy z 'zapytaj o cenę'")
    
    # Usuń duplikaty na podstawie URL (jeśli są)
    before_duplicates = len(df_cleaned)
    df_cleaned = df_cleaned.drop_duplicates(subset=['url'], keep='first')
    removed_duplicates = before_duplicates - len(df_cleaned)
    if removed_duplicates > 0:
        print(f"Usunięto {removed_duplicates} duplikatów")
    
    final_count = len(df_cleaned)
    print(f"\nKońcowa liczba wierszy: {final_count}")
    print(f"Usunięto łącznie: {initial_count - final_count} wierszy ({(initial_count - final_count) / initial_count * 100:.1f}%)")
    
    # Statystyki po czyszczeniu
    print("\nStatystyki po czyszczeniu:")
    print(f"  - Wiersze z NaN w rooms: {df_cleaned['rooms'].isna().sum()}")
    print(f"  - Wiersze z NaN w area: {df_cleaned['area'].isna().sum()}")
    print(f"  - Wiersze z NaN w price_total_zl: {df_cleaned['price_total_zl'].isna().sum()}")
    print(f"  - Wiersze z NaN w price_sqm_zl: {df_cleaned['price_sqm_zl'].isna().sum()}")
    
    # Zapisz wyczyszczone dane
    if output_file is None:
        # Generuj nazwę pliku wyjściowego w tym samym katalogu co input
        base_name = os.path.splitext(input_file)[0]
        # Usuń '_detailed' z nazwy jeśli istnieje
        base_name = base_name.replace('_detailed', '')
        output_file = f"{base_name}_cleaned.csv"
    
    df_cleaned.to_csv(output_file, index=False)
    print(f"\nWyczyszczone dane zapisano do: {output_file}")
    
    return df_cleaned

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Skrypt do czyszczenia danych zeskrapowanych z adresowo.pl',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Przykłady użycia:
  # Wyczyść dane z domyślnymi ustawieniami
  python clean_data.py ogloszenia_warszawa.csv
  
  # Wyczyść z własnym progiem minimalnych pól
  python clean_data.py ogloszenia_lodz.csv --min-fields 6
  
  # Wyczyść i usuń ogłoszenia z "zapytaj o cenę"
  python clean_data.py ogloszenia_wroclaw.csv --remove-price-ask
  
  # Wyczyść z własną nazwą pliku wyjściowego
  python clean_data.py ogloszenia_warszawa.csv --output warszawa_clean.csv
        '''
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Ścieżka do pliku CSV z surowymi danymi'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Ścieżka do pliku wyjściowego CSV. Domyślnie: {input}_cleaned.csv'
    )
    
    parser.add_argument(
        '--min-fields',
        type=int,
        default=5,
        help='Minimalna liczba niepustych pól wymagana do zachowania wiersza. Domyślnie: 5'
    )
    
    parser.add_argument(
        '--remove-price-ask',
        action='store_true',
        help='Usuń wiersze z "zapytaj o cenę" w kolumnie price_total_zl'
    )
    
    args = parser.parse_args()
    
    # Sprawdź czy plik istnieje
    if not os.path.exists(args.input_file):
        print(f"Błąd: Plik {args.input_file} nie istnieje!")
        exit(1)
    
    clean_scraped_data(
        args.input_file,
        args.output,
        args.min_fields,
        args.remove_price_ask
    )

