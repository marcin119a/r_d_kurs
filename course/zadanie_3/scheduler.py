import schedule, time
from datetime import datetime
from scrape import main as scrape_main

def run_scraper():
    print(f"Uruchamianie scrapera o {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    scrape_main()
    print(f"Zakończono scrapera o {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

#schedule.every(24).hours.do(run_scraper)
schedule.every().day.at("15:48").do(run_scraper)

while True:
    schedule.run_pending()
    time.sleep(60)


