import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Globalna zmienna do przechowywania informacji o czcionkach
FONT_NORMAL = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'

# Rejestracja czcionek z obsługą polskich znaków
def register_fonts():
    """Rejestruje czcionki z pełnym wsparciem dla polskich znaków"""
    global FONT_NORMAL, FONT_BOLD
    
    try:
        from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
        from reportlab.pdfbase.ttfonts import TTFont
        import os
        
        # Ścieżka do katalogu ze skryptem
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Najpierw spróbuj użyć czcionek Lato z lokalnego katalogu
        # Sprawdź zarówno bezpośrednio w katalogu, jak i w podfolderze Lato/
        lato_paths = {
            'Lato-Regular': [
                os.path.join(script_dir, 'Lato', 'Lato-Regular.ttf'),
                os.path.join(script_dir, 'Lato-Regular.ttf'),
            ],
            'Lato-Bold': [
                os.path.join(script_dir, 'Lato', 'Lato-Bold.ttf'),
                os.path.join(script_dir, 'Lato-Bold.ttf'),
            ],
            'Lato-BoldItalic': [
                os.path.join(script_dir, 'Lato', 'Lato-BoldItalic.ttf'),
                os.path.join(script_dir, 'Lato-BoldItalic.ttf'),
            ],
        }
        
        lato_registered = {}
        for font_name, paths in lato_paths.items():
            registered = False
            for path in paths:
                try:
                    if os.path.exists(path):
                        registerFont(TTFont(font_name, path))
                        lato_registered[font_name] = True
                        print(f"✓ Zarejestrowano czcionkę: {font_name} ({os.path.basename(path)})")
                        registered = True
                        break
                except Exception as e:
                    continue
            
            if not registered:
                lato_registered[font_name] = False
        
        # Sprawdź czy mamy wystarczające czcionki Lato
        if lato_registered.get('Lato-Regular') and lato_registered.get('Lato-Bold'):
            registerFontFamily('Lato', normal='Lato-Regular', bold='Lato-Bold')
            FONT_NORMAL = 'Lato-Regular'
            FONT_BOLD = 'Lato-Bold'
            print("✓ Używam czcionek Lato (pełne wsparcie dla polskich znaków)\n")
            return True
        elif lato_registered.get('Lato-Bold'):
            # Jeśli mamy tylko Lato-Bold, użyj jej dla obu
            FONT_NORMAL = 'Lato-Bold'
            FONT_BOLD = 'Lato-Bold'
            print("✓ Używam czcionki Lato-Bold (tylko pogrubienie dostępne)")
            print("💡 Wskazówka: Dodaj pliki Lato-Regular.ttf i Lato-Bold.ttf do katalogu documents/\n")
            return True
        else:
            print("⚠ Nie znaleziono kompletnych czcionek Lato")
            if lato_registered.get('Lato-BoldItalic'):
                print("   Znaleziono: Lato-BoldItalic.ttf")
            print("   Brakuje: Lato-Regular.ttf, Lato-Bold.ttf")
            print("💡 Pobierz czcionki Lato z: https://fonts.google.com/specimen/Lato\n")
        
        # Próbuj użyć czcionek systemowych DejaVu jako opcja rezerwowa
        print("Szukam czcionek systemowych DejaVu...")
        font_paths = {
            'DejaVuSans': [
                '/System/Library/Fonts/Supplemental/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/Library/Fonts/DejaVuSans.ttf',
            ],
            'DejaVuSans-Bold': [
                '/System/Library/Fonts/Supplemental/DejaVuSans-Bold.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                '/Library/Fonts/DejaVuSans-Bold.ttf',
            ]
        }
        
        fonts_registered = True
        for font_name, paths in font_paths.items():
            registered = False
            for path in paths:
                try:
                    registerFont(TTFont(font_name, path))
                    registered = True
                    print(f"✓ Zarejestrowano czcionkę: {font_name}")
                    break
                except Exception as e:
                    continue
            
            if not registered:
                fonts_registered = False
                break
        
        if fonts_registered:
            registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans-Bold')
            FONT_NORMAL = 'DejaVuSans'
            FONT_BOLD = 'DejaVuSans-Bold'
            print("✓ Używam czcionek DejaVu Sans (pełne wsparcie Unicode)\n")
            return True
        else:
            print("⚠ Nie znaleziono czcionek DejaVu")
            print("✓ Używam wbudowanych czcionek Helvetica (podstawowe wsparcie dla polskich znaków)\n")
            FONT_NORMAL = 'Helvetica'
            FONT_BOLD = 'Helvetica-Bold'
            return False
        
    except Exception as e:
        print(f"⚠ Błąd przy rejestracji czcionek: {e}")
        print("✓ Używam wbudowanych czcionek Helvetica\n")
        FONT_NORMAL = 'Helvetica'
        FONT_BOLD = 'Helvetica-Bold'
        return False

def create_property_pdf(row, index, output_dir='documents/pdfs'):
    """Tworzy ładny PDF dla pojedynczej oferty mieszkania"""
    
    # Upewnij się, że katalog istnieje
    os.makedirs(output_dir, exist_ok=True)
    
    # Nazwa pliku
    filename = f"{output_dir}/oferta_{index+1:02d}_mieszkanie.pdf"
    
    # Tworzenie dokumentu PDF
    doc = SimpleDocTemplate(filename, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    # Elementy do dodania
    elements = []
    
    # Style
    styles = getSampleStyleSheet()
    
    # Customowy styl dla tytułu (obsługuje polskie znaki)
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E40AF'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName=FONT_BOLD
    )
    
    # Styl dla nagłówków sekcji
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#3B82F6'),
        spaceAfter=12,
        spaceBefore=20,
        fontName=FONT_BOLD
    )
    
    # Styl dla tekstu
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6,
        fontName=FONT_NORMAL
    )
    
    # Styl dla opisu
    description_style = ParagraphStyle(
        'Description',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName=FONT_NORMAL,
        leading=16
    )
    
    # Tytuł główny
    title_text = f"Oferta Mieszkania #{index+1}"
    title = Paragraph(title_text, title_style)
    elements.append(title)
    
    elements.append(Spacer(1, 0.5*cm))
    
    # Placeholder dla zdjęcia - możesz później dodać ładowanie obrazów
    # Na razie skupiamy się na czystym, czytelnym formacie
    elements.append(Spacer(1, 0.3*cm))
    
    # Lokalizacja
    location_header = Paragraph("📍 Lokalizacja", section_style)
    elements.append(location_header)
    
    location = f"{row['locality']}, {row['street']}"
    location_para = Paragraph(location, normal_style)
    elements.append(location_para)
    elements.append(Spacer(1, 0.5*cm))
    
    # Treść ogłoszenia - generowana na podstawie danych
    content_header = Paragraph("📝 Opis Oferty", section_style)
    elements.append(content_header)
    
    # Generuj treść opisu
    rooms_num = int(row['rooms']) if pd.notna(row['rooms']) else 0
    area_num = row['area'] if pd.notna(row['area']) else 0
    price_num = int(row['price_total_zl']) if pd.notna(row['price_total_zl']) else 0
    price_sqm = int(row['price_sqm_zl']) if pd.notna(row['price_sqm_zl']) else 0
    
    rooms_text = {
        1: "jednopokojowe",
        2: "dwupokojowe", 
        3: "trzypokojowe",
        4: "czteropokojowe",
        5: "pięciopokojowe"
    }.get(rooms_num, f"{rooms_num}-pokojowe")
    
    description_text = f"""
    Do sprzedaży {rooms_text} mieszkanie o powierzchni {area_num:.1f} m² 
    w atrakcyjnej lokalizacji: {row['locality']}, {row['street']}. 
    Mieszkanie oferuje komfortową przestrzeń życiową idealną dla osób szukających 
    wysokiego standardu w doskonałej lokalizacji.
    <br/><br/>
    Cena całkowita: <b>{price_num:,}</b> zł (cena za m²: <b>{price_sqm:,}</b> zł).
    <br/><br/>
    {row['owner_type']}. Ogłoszenie zostało opublikowane: {row['date_posted']}.
    <br/><br/>
    Zapraszamy do kontaktu w celu uzyskania szczegółowych informacji oraz umówienia 
    się na prezentację nieruchomości. W ogłoszeniu dostępnych jest {int(row['photo_count']) if pd.notna(row['photo_count']) else 0} zdjęć 
    prezentujących walory mieszkania.
    """.replace(',', ' ')
    
    description_para = Paragraph(description_text, description_style)
    elements.append(description_para)
    elements.append(Spacer(1, 0.5*cm))
    
    # Szczegóły mieszkania - tabela
    details_header = Paragraph("🏠 Szczegóły Mieszkania", section_style)
    elements.append(details_header)
    
    # Przygotowanie danych do tabeli
    rooms_str = f"{int(row['rooms'])}" if pd.notna(row['rooms']) else "N/A"
    area_str = f"{row['area']:.1f}" if pd.notna(row['area']) else "N/A"
    price_str = f"{int(row['price_total_zl']):,}".replace(',', ' ') if pd.notna(row['price_total_zl']) else "N/A"
    price_sqm_str = f"{int(row['price_sqm_zl']):,}".replace(',', ' ') if pd.notna(row['price_sqm_zl']) else "N/A"
    
    data = [
        ['Liczba pokoi:', rooms_str, 'Powierzchnia:', f"{area_str} m²"],
        ['Cena całkowita:', f"{price_str} zł", 'Cena za m²:', f"{price_sqm_str} zł"],
    ]
    
    # Tworzenie tabeli
    table = Table(data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#DBEAFE')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#DBEAFE')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1F2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (2, 0), (2, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NORMAL),
        ('FONTNAME', (3, 0), (3, -1), FONT_NORMAL),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#93C5FD'))
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Informacje dodatkowe o nieruchomości
    info_header = Paragraph("🏢 Informacje o Budynku", section_style)
    elements.append(info_header)
    
    # Buduj listę informacji o budynku
    building_info_data = []
    
    # Piętro
    if pd.notna(row.get('floor')):
        building_info_data.append(['Piętro:', str(row['floor'])])
    
    # Rok budowy
    if pd.notna(row.get('year_built')):
        building_info_data.append(['Rok budowy:', str(int(row['year_built']))])
    
    # Typ budynku
    if pd.notna(row.get('building_type')):
        building_info_data.append(['Typ budynku:', str(row['building_type'])])
    
    # Forma własności
    if pd.notna(row.get('ownership_type')):
        building_info_data.append(['Forma własności:', str(row['ownership_type'])])
    
    # Jeśli są jakieś informacje, wyświetl tabelę
    if building_info_data:
        building_table = Table(building_info_data, colWidths=[6*cm, 10*cm])
        building_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E0E7FF')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1F2937')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
            ('FONTNAME', (1, 0), (1, -1), FONT_NORMAL),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#C7D2FE'))
        ]))
        elements.append(building_table)
        elements.append(Spacer(1, 0.5*cm))
    
    # Udogodnienia
    amenities_header = Paragraph("✨ Udogodnienia", section_style)
    elements.append(amenities_header)
    
    amenities_data = []
    
    # Typ kuchni
    if pd.notna(row.get('kitchen_type')):
        amenities_data.append(['Kuchnia:', str(row['kitchen_type'])])
    
    # Typ okien
    if pd.notna(row.get('window_type')):
        amenities_data.append(['Okna:', str(row['window_type'])])
    
    # Piwnica
    if pd.notna(row.get('has_basement')):
        basement = 'Tak' if str(row['has_basement']).lower() == 'tak' else 'Nie'
        amenities_data.append(['Piwnica:', basement])
    
    # Parking
    if pd.notna(row.get('has_parking')):
        parking = 'Tak' if str(row['has_parking']).lower() == 'tak' else 'Nie'
        amenities_data.append(['Parking:', parking])
    
    # Wyposażenie
    if pd.notna(row.get('equipment')) and row.get('equipment'):
        equipment_text = str(row['equipment'])
        # Ogranicz długość do maks 100 znaków
        if len(equipment_text) > 100:
            equipment_text = equipment_text[:97] + '...'
        amenities_data.append(['Wyposażenie:', equipment_text])
    
    if amenities_data:
        amenities_table = Table(amenities_data, colWidths=[6*cm, 10*cm])
        amenities_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#D1FAE5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1F2937')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
            ('FONTNAME', (1, 0), (1, -1), FONT_NORMAL),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#A7F3D0'))
        ]))
        elements.append(amenities_table)
        elements.append(Spacer(1, 0.5*cm))
    
    # Informacje o ogłoszeniu
    info_header2 = Paragraph("ℹ️ Informacje o Ogłoszeniu", section_style)
    elements.append(info_header2)
    
    owner_type = row['owner_type'] if pd.notna(row['owner_type']) else "Brak informacji"
    date_posted = row['date_posted'] if pd.notna(row['date_posted']) else "Brak daty"
    photo_count = int(row['photo_count']) if pd.notna(row['photo_count']) else 0
    
    info_data = [
        ['Typ ogłoszeniodawcy:', owner_type],
        ['Data publikacji:', date_posted],
        ['Liczba zdjęć:', str(photo_count)],
    ]
    
    info_table = Table(info_data, colWidths=[6*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FEF3C7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1F2937')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NORMAL),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FDE68A'))
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Link do ogłoszenia
    if pd.notna(row['url']):
        link_header = Paragraph("🔗 Link do Ogłoszenia", section_style)
        elements.append(link_header)
        
        url_style = ParagraphStyle(
            'URLStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2563EB'),
            fontName=FONT_NORMAL
        )
        link_para = Paragraph(f'<a href="{row["url"]}">{row["url"]}</a>', url_style)
        elements.append(link_para)
    
    # Footer
    elements.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#6B7280'),
        alignment=TA_CENTER,
        fontName=FONT_NORMAL
    )
    footer = Paragraph("Wygenerowano automatycznie | Oferty mieszkań w Łodzi", footer_style)
    elements.append(footer)
    
    # Budowanie PDF
    doc.build(elements)
    print(f"✓ Utworzono PDF: {filename}")
    
    return filename

def main():
    """Główna funkcja generująca PDFy"""
    
    # Zarejestruj czcionki z obsługą polskich znaków
    print("Rejestrowanie czcionek z obsługą polskich znaków...\n")
    register_fonts()
    
    # Wczytaj dane z pliku detailed (zawiera więcej szczegółów)
    csv_path = '/Users/mw/r_d_kurs/scraper/data/ogloszenia_lodz_detailed.csv'
    df = pd.read_csv(csv_path)
    
    print(f"\nWczytano {len(df)} ofert z CSV (plik detailed z dodatkowymi szczegółami)")
    print(f"\nGenerowanie 10 PDFów...\n")
    
    # Wybierz 10 różnorodnych ofert (różne dzielnice, różne liczby pokoi)
    # Sortuj po różnych kryteriach dla lepszej różnorodności
    sample_indices = []
    
    # Weź po kilka z różnych kategorii
    for rooms in [1, 2, 3, 4, 5]:
        room_offers = df[df['rooms'] == rooms]
        if len(room_offers) > 0:
            sample_indices.append(room_offers.index[0])
        if len(sample_indices) >= 10:
            break
    
    # Jeśli nie mamy 10, dodaj losowe
    while len(sample_indices) < 10 and len(sample_indices) < len(df):
        idx = len(sample_indices)
        if idx < len(df):
            sample_indices.append(df.index[idx])
    
    # Generuj PDFy
    generated_files = []
    for i, idx in enumerate(sample_indices[:10]):
        row = df.iloc[idx]
        try:
            filename = create_property_pdf(row, i)
            generated_files.append(filename)
        except Exception as e:
            print(f"✗ Błąd przy tworzeniu PDF {i+1}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✓ Wygenerowano {len(generated_files)} PDFów w katalogu documents/pdfs/")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

