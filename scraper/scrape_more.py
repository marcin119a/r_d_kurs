import requests
import csv
from bs4 import BeautifulSoup
import time
import argparse
import re

# Stałe
BASE_URL = 'https://adresowo.pl'

# Nagłówki HTTP, aby udawać przeglądarkę
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Nagłówki CSV rozszerzone
CSV_HEADERS = [
    'locality',
    'street',
    'rooms',
    'area',
    'price_total_zl',
    'price_sqm_zl',
    'owner_type',
    'date_posted',
    'photo_count',
    'url',
    'image_url',
    # Nowe pola ze szczegółowej strony
    'city_district',
    'full_address',
    'floor',
    'year_built',
    'building_type',
    'price_per_sqm_detailed',
    'description_text',
    'has_basement',
    'has_parking',
    'kitchen_type',
    'window_type',
    'ownership_type',
    'equipment',
    'latitude',
    'longitude'
]


def clean_text(text):
    """Czyści tekst z nadmiarowych białych znaków i znaków specjalnych."""
    if not text:
        return ''
    # Usuń \xa0 (nbsp), wielokrotne spacje, nowe linie
    text = text.replace('\xa0', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_equipment(text):
    """Wyciąga listę wyposażenia z tekstu."""
    if not text:
        return ''
    
    text_lower = text.lower()
    equipment_items = []
    
    # Lista możliwych urządzeń
    appliances = [
        'lodówka', 'lodowka', 'lodówkę',
        'zmywarka', 'zmywarkę',
        'pralka', 'pralkę',
        'suszarka', 'suszarkę',
        'piekarnik',
        'kuchenka', 'kuchenkę',
        'mikrofalówka', 'mikrofalowka',
        'telewizor', 'tv',
        'klimatyzacja', 'klimatyzacje',
        'internet',
        'wifi', 'wi-fi'
    ]
    
    for appliance in appliances:
        if appliance in text_lower:
            # Dodaj wersję podstawową (bez polskich znaków końcowych)
            base = appliance.rstrip('ęę')
            if base not in [item.rstrip('ęę') for item in equipment_items]:
                equipment_items.append(appliance)
    
    if equipment_items:
        return 'Wyposażenie: ' + ', '.join(sorted(set(equipment_items)))
    return ''


def parse_offer_details(soup):
    """
    Pobiera szczegółowe dane z pojedynczej strony ogłoszenia.
    Zwraca słownik z dodatkowymi danymi.
    """
    details = {
        'city_district': '',
        'full_address': '',
        'floor': '',
        'year_built': '',
        'building_type': '',
        'price_per_sqm_detailed': '',
        'description_text': '',
        'has_basement': '',
        'has_parking': '',
        'kitchen_type': '',
        'window_type': '',
        'ownership_type': '',
        'equipment': '',
        'latitude': '',
        'longitude': ''
    }
    
    try:
        # --- offer-header-container ---
        header_container = soup.select_one('.offer-header-container')
        if header_container:
            # Miasto i dzielnica
            city_span = header_container.select_one('.offer-header__city')
            if city_span:
                details['city_district'] = clean_text(city_span.get_text())
            
            # Ulica
            street_span = header_container.select_one('.offer-header__street')
            if street_span:
                details['full_address'] = clean_text(street_span.get_text())
            
            # Piętro, rok budowy, cena za m² - bardziej precyzyjne parsowanie
            summary_items = header_container.select('.offer-summary__item')
            for item in summary_items:
                # Pobierz cały tekst z item
                full_text = clean_text(item.get_text())
                
                # Szukamy w div role="row" które nie mają klasy offer-summary__second-row
                rows = item.select('div[role="row"]')
                
                for row in rows:
                    row_text = clean_text(row.get_text())
                    
                    # Cena za m²
                    if 'Cena za m²' in row_text or 'Cena za m2' in row_text:
                        value = row.select_one('.offer-summary__value')
                        if value:
                            details['price_per_sqm_detailed'] = clean_text(value.get_text())
                    
                    # Piętro
                    elif 'Piętro' in row_text:
                        value = row.select_one('.offer-summary__value')
                        if value:
                            details['floor'] = clean_text(value.get_text())
                    
                    # Rok budowy
                    elif 'Rok budowy' in row_text:
                        value = row.select_one('.offer-summary__value')
                        if value:
                            details['year_built'] = clean_text(value.get_text())
        
        # --- offer-description ---
        description_div = soup.select_one('.offer-description')
        if description_div:
            # Opis tekstowy
            desc_text = description_div.select_one('.offer-description__text')
            if desc_text:
                # Usuń linki i zostaw czysty tekst
                for a in desc_text.find_all('a'):
                    a.replace_with(a.get_text())
                details['description_text'] = clean_text(desc_text.get_text())
            
            # Szczegóły z listy
            summary_list = description_div.select('.offer-description__summary li')
            
            # Zbierz cały tekst ze wszystkich li
            all_summary_text = ' '.join([li.get_text().lower() for li in summary_list])
            
            for li in summary_list:
                text = li.get_text()
                text_lower = text.lower()
                
                # Typ budynku - sprawdzamy najpierw w tym li
                if 'kamienica' in text_lower and not details['building_type']:
                    details['building_type'] = 'kamienica'
                elif 'blok' in text_lower and not details['building_type']:
                    details['building_type'] = 'blok'
                elif 'apartamentowiec' in text_lower and not details['building_type']:
                    details['building_type'] = 'apartamentowiec'
                elif 'dom' in text_lower and 'budyn' in text_lower and not details['building_type']:
                    details['building_type'] = 'dom'
                
                # Piętro - wyciągamy z tekstu typu "2 piętro" lub "parter"
                if not details['floor']:
                    if 'piętro' in text_lower or 'piętrze' in text_lower:
                        # Szukamy numeru przed słowem piętro
                        floor_match = re.search(r'(\d+)\s*(?:piętro|piętrze)', text_lower)
                        if floor_match:
                            details['floor'] = floor_match.group(1)
                        elif 'parter' in text_lower:
                            details['floor'] = 'parter'
                
                # Rok budowy - wyciągamy z tekstu
                if not details['year_built']:
                    year_match = re.search(r'\b(19\d{2}|20\d{2})\s*rok', text_lower)
                    if year_match:
                        details['year_built'] = year_match.group(1)
                
                # Piwnica
                if 'piwnica' in text_lower and not details['has_basement']:
                    details['has_basement'] = 'tak'
                
                # Parking
                if ('miejsce parkingowe' in text_lower or 
                    'parking' in text_lower or 
                    'garaż' in text_lower) and not details['has_parking']:
                    details['has_parking'] = 'tak'
                
                # Typ kuchni
                if not details['kitchen_type']:
                    if 'osobna kuchnia' in text_lower or 'oddzielna kuchnia' in text_lower:
                        details['kitchen_type'] = 'osobna'
                    elif 'aneks kuchenny' in text_lower:
                        details['kitchen_type'] = 'aneks'
                    elif 'aneks' in text_lower and ('kuchni' in text_lower or 'salon' in text_lower):
                        details['kitchen_type'] = 'aneks'
                
                # Okna
                if not details['window_type']:
                    if 'okna plastikowe' in text_lower or 'pvc' in text_lower or 'pcv' in text_lower:
                        details['window_type'] = 'plastikowe'
                    elif 'okna drewniane' in text_lower:
                        details['window_type'] = 'drewniane'
                
                # Własność
                if not details['ownership_type']:
                    if 'odrębna własność' in text_lower or 'własność' in text_lower and 'księga' in text_lower:
                        details['ownership_type'] = 'własność'
                    elif 'spółdzielcze własnościowe' in text_lower:
                        details['ownership_type'] = 'spółdzielcze własnościowe'
                    elif 'spółdzielcze lokatorskie' in text_lower:
                        details['ownership_type'] = 'spółdzielcze lokatorskie'
                    elif 'własnościowe' in text_lower and 'mieszkanie' in text_lower:
                        details['ownership_type'] = 'własność'
                
                # Wyposażenie - jeśli jest explicit w tekście
                if 'wyposażenie:' in text_lower and not details['equipment']:
                    equipment_start = text.lower().find('wyposażenie:')
                    equipment_text = text[equipment_start:]
                    details['equipment'] = clean_text(equipment_text)
            
            # Jeśli nie znaleziono explicit wyposażenia, spróbuj wyciągnąć z całego opisu
            if not details['equipment'] and details['description_text']:
                extracted_equipment = extract_equipment(details['description_text'])
                if extracted_equipment:
                    details['equipment'] = extracted_equipment
        
        # --- Koordynaty z JSON-LD ---
        script_tags = soup.find_all('script', type='application/ld+json')
        for script_tag in script_tags:
            try:
                import json
                if script_tag.string:
                    json_data = json.loads(script_tag.string)
                    
                    # Sprawdź różne struktury JSON-LD
                    if '@graph' in json_data and len(json_data['@graph']) > 0:
                        geo = json_data['@graph'][0].get('geo', {})
                        if geo:
                            details['latitude'] = str(geo.get('latitude', ''))
                            details['longitude'] = str(geo.get('longitude', ''))
                            break
                    elif 'geo' in json_data:
                        geo = json_data.get('geo', {})
                        details['latitude'] = str(geo.get('latitude', ''))
                        details['longitude'] = str(geo.get('longitude', ''))
                        break
            except Exception as json_error:
                continue
        
        # Jeśli nie znaleziono piętra w summary, spróbuj w opisie
        if not details['floor']:
            # Szukaj w całym opisie
            desc_full = soup.get_text()
            desc_lower = desc_full.lower()
            
            if 'parter' in desc_lower:
                details['floor'] = 'parter'
            else:
                # Szukaj wzorców jak "na 2 piętrze", "2. piętro", etc.
                floor_patterns = [
                    r'na\s+(\d+)\s+piętrze',
                    r'(\d+)\s*\.\s*piętro',
                    r'piętro[:\s]+(\d+)',
                    r'(\d+)\s+piętro',
                    r'(\d+)\s+z\s+\d+'  # "4 z 10" pattern
                ]
                for pattern in floor_patterns:
                    match = re.search(pattern, desc_lower)
                    if match:
                        details['floor'] = match.group(1)
                        break
        
        # Jeśli wciąż brak roku budowy, spróbuj wyciągnąć z całego tekstu
        if not details['year_built']:
            desc_full = soup.get_text()
            # Szukaj lat w formacie 19XX lub 20XX
            year_patterns = [
                r'rok budowy[:\s]+(19\d{2}|20\d{2})',
                r'z\s+(19\d{2}|20\d{2})\s+roku',
                r'budynek\s+z\s+(19\d{2}|20\d{2})',
                r'\b(19\d{2}|20\d{2})\s+rok\b'
            ]
            for pattern in year_patterns:
                match = re.search(pattern, desc_full.lower())
                if match:
                    year = match.group(1)
                    # Sprawdź czy rok jest sensowny (1900-2030)
                    if 1900 <= int(year) <= 2030:
                        details['year_built'] = year
                        break
        
        # Dodatkowe wykrywanie budynków typu "winda" sugeruje blok lub apartamentowiec
        if not details['building_type']:
            desc_full = soup.get_text().lower()
            if 'apartamentowiec' in desc_full:
                details['building_type'] = 'apartamentowiec'
            elif 'kamienica' in desc_full:
                details['building_type'] = 'kamienica'
            elif 'blok' in desc_full or 'winda' in desc_full:
                details['building_type'] = 'blok'
        
    except Exception as e:
        print(f"  Błąd podczas parsowania szczegółów: {e}")
    
    return details


def process_csv_file(input_file, output_file, delay=1.0):
    """
    Wczytuje plik CSV z ogłoszeniami, pobiera szczegóły z każdej strony
    i zapisuje rozszerzone dane do nowego pliku CSV.
    
    Args:
        input_file (str): Ścieżka do pliku CSV wejściowego
        output_file (str): Ścieżka do pliku CSV wyjściowego
        delay (float): Opóźnienie między requestami w sekundach
    """
    print(f"Wczytywanie danych z: {input_file}")
    
    # Wczytaj dane z pliku CSV
    rows_to_process = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows_to_process = list(reader)
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {input_file}")
        return
    except Exception as e:
        print(f"Błąd podczas wczytywania pliku: {e}")
        return
    
    print(f"Znaleziono {len(rows_to_process)} ogłoszeń do przetworzenia.")
    
    # Przetwarzanie każdego URL-a
    all_data = []
    
    with requests.Session() as session:
        session.headers.update(HTTP_HEADERS)
        
        for idx, row in enumerate(rows_to_process, 1):
            url = row.get('url', '')
            if not url:
                print(f"[{idx}/{len(rows_to_process)}] Pominięto - brak URL")
                continue
            
            print(f"[{idx}/{len(rows_to_process)}] Przetwarzanie: {url}")
            
            try:
                response = session.get(url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Pobierz szczegóły
                details = parse_offer_details(soup)
                
                # Połącz dane podstawowe z szczegółowymi
                combined_row = {
                    'locality': row.get('locality', ''),
                    'street': row.get('street', ''),
                    'rooms': row.get('rooms', ''),
                    'area': row.get('area', ''),
                    'price_total_zl': row.get('price_total_zl', ''),
                    'price_sqm_zl': row.get('price_sqm_zl', ''),
                    'owner_type': row.get('owner_type', ''),
                    'date_posted': row.get('date_posted', ''),
                    'photo_count': row.get('photo_count', ''),
                    'url': url,
                    'image_url': row.get('image_url', ''),
                    **details  # Dodaj szczegóły
                }
                
                all_data.append(combined_row)
                
                # Opóźnienie między requestami
                time.sleep(delay)
                
            except requests.RequestException as e:
                print(f"  Błąd podczas pobierania strony: {e}")
                # Dodaj wiersz z podstawowymi danymi, bez szczegółów
                combined_row = {header: row.get(header, '') for header in CSV_HEADERS}
                all_data.append(combined_row)
                continue
            except Exception as e:
                print(f"  Nieoczekiwany błąd: {e}")
                continue
    
    # Zapisz do pliku CSV
    if all_data:
        print(f"\nZapisywanie {len(all_data)} ogłoszeń do pliku {output_file}...")
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                writer.writeheader()
                writer.writerows(all_data)
            print(f"Pomyślnie zapisano dane w pliku: {output_file}")
        except IOError as e:
            print(f"Błąd podczas zapisu do pliku {output_file}: {e}")
    else:
        print("\nNie udało się przetworzyć żadnych danych.")


def main():
    parser = argparse.ArgumentParser(
        description='Scraper szczegółowych informacji z ogłoszeń adresowo.pl',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Przykłady użycia:
  # Przetwórz plik z Łodzi
  python scrape_more.py --input ogloszenia_lodz.csv --output ogloszenia_lodz_detailed.csv
  
  # Przetwórz plik z Warszawy z krótszym opóźnieniem
  python scrape_more.py --input ogloszenia_warszawa.csv --output ogloszenia_warszawa_detailed.csv --delay 0.5
        '''
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Ścieżka do pliku CSV wejściowego (z ogłoszeniami)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Ścieżka do pliku CSV wyjściowego (z szczegółowymi danymi)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=0.1,
        help='Opóźnienie między requestami w sekundach (domyślnie: 0.1)'
    )
    
    args = parser.parse_args()
    
    process_csv_file(args.input, args.output, args.delay)


if __name__ == "__main__":
    main()

