from parser.parser import parse_holidays, parse_events
from pw.client import PlaywrightClient
from storage.db import init_db, close_connection
from storage.holiday_repo import insert_holidays_bulk
from storage.event_repo import insert_events_bulk
import argparse
import json
from datetime import date, timedelta
import time
import random

MAX_RETRIES = 3

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

MONTH_NAMES_RU = {
    1: "yanvar", 2: "fevral", 3: "mart",
    4: "aprel", 5: "may", 6: "iyun",
    7: "iyul", 8: "avgust", 9: "sentyabr",
    10: "oktyabr", 11: "noyabr", 12: "dekabr",
}


def main(start_date: date, end_date: date):
    init_db()

    next_long_pause_in = random.randint(7, 10)
    days_counter = 0

    with PlaywrightClient(
        headless=False,
        user_agent=USER_AGENT,
        viewport={"width": 1280, "height": 800},
    ) as context:
        current = start_date
        while current <= end_date:
            days_counter += 1
            month_name = MONTH_NAMES_RU[current.month]
            url = f"https://kakoysegodnyaprazdnik.ru/baza/{month_name}/{current.day}"
            print(f"{current} Парсим {url}")

            iso_date = current.isoformat()
            success = False

            for attempt in range(1, MAX_RETRIES + 1):
                page = context.new_page()
                try:
                    print(f"Попытка {attempt}/{MAX_RETRIES}")

                    holidays = parse_holidays(page, url, iso_date)
                    events = parse_events(page, iso_date)

                    insert_holidays_bulk(holidays)
                    insert_events_bulk(events)

                    for h in holidays:
                        print(json.dumps({
                            "date": h.date,
                            "name": h.name,
                            "category": h.category,
                            "country": h.country
                        }, ensure_ascii=False))

                    for e in events:
                        print(json.dumps({
                            "date": e.date,
                            "year": e.year,
                            "name": e.name
                        }, ensure_ascii=False))

                    success = True
                    page.close()
                    print("День успешно обработан")
                    break

                except Exception as e:
                    page.close()
                    print(f"Ошибка: {e}")
                    if attempt < MAX_RETRIES:
                        retry_sleep = random.uniform(5, 10) * attempt
                        print(f"Повтор через {int(retry_sleep)} сек")
                        time.sleep(retry_sleep)

            if not success:
                print(f"День {current} пропущен после {MAX_RETRIES} попыток")

            time.sleep(random.uniform(2, 5))

            if days_counter >= next_long_pause_in:
                long_sleep = random.uniform(30, 90)
                print(f"Долгая пауза {int(long_sleep)} сек")
                time.sleep(long_sleep)

                days_counter = 0
                next_long_pause_in = random.randint(7, 10)

            current += timedelta(days=1)

    close_connection()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Парсер праздников и событий")
    parser.add_argument(
        "--start",
        type=date.fromisoformat,
        default=date(2026, 3, 1),
        help="Начальная дата (YYYY-MM-DD), по умолчанию 2026-03-01",
    )
    parser.add_argument(
        "--end",
        type=date.fromisoformat,
        default=date(2026, 3, 31),
        help="Конечная дата (YYYY-MM-DD), по умолчанию 2026-03-31",
    )
    args = parser.parse_args()
    main(args.start, args.end)
