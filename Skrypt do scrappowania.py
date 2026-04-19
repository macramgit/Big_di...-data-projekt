import asyncio
import random
import re
from datetime import datetime
import pandas as pd
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout



# KONFIGURACJA

CITIES = {
    "warszawa": "https://gratka.pl/nieruchomosci/mieszkania/warszawa",
    "krakow": "https://gratka.pl/nieruchomosci/mieszkania/krakow",
    "wroclaw": "https://gratka.pl/nieruchomosci/mieszkania/wroclaw",
    "poznan": "https://gratka.pl/nieruchomosci/mieszkania/poznan",
    "gdansk": "https://gratka.pl/nieruchomosci/mieszkania/gdansk",
    "lodz": "https://gratka.pl/nieruchomosci/mieszkania/lodz",
}

MAX_PAGES_PER_CITY = 40
HEADLESS = True
OUTPUT_FILE = "gratka_mieszkania_listing.csv"

DELAY_MIN = 1.2
DELAY_MAX = 2.5



# HELPERY

async def random_delay():
    await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


async def accept_cookies(page):
    selectors = [
        'button:has-text("Akceptuję")',
        'button:has-text("Zaakceptuj")',
        'button:has-text("Akceptuj")',
        'button:has-text("Accept")',
        'button[id*="accept"]',
        'button[class*="accept"]',
    ]
    for selector in selectors:
        try:
            await page.click(selector, timeout=2000)
            return
        except Exception:
            pass


async def text_or_none(el):
    if not el:
        return None
    try:
        text = (await el.inner_text()).strip()
        return re.sub(r"\s+", " ", text)
    except Exception:
        return None


def parse_price(text):
    if not text:
        return None
    match = re.search(r"(\d[\d\s]*)\s*zł(?!/m²)", text, re.IGNORECASE)
    if not match:
        return None
    return float(re.sub(r"\s+", "", match.group(1)))


def parse_price_per_m2(text):
    if not text:
        return None
    match = re.search(r"(\d[\d\s]*)\s*zł/m²", text, re.IGNORECASE)
    if not match:
        return None
    return float(re.sub(r"\s+", "", match.group(1)))


def parse_area(text):
    if not text:
        return None
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*m²", text, re.IGNORECASE)
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def parse_rooms(text):
    if not text:
        return None
    match = re.search(r"(\d+)\s*pok", text, re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def parse_floor(text):
    if not text:
        return None

    text = text.lower().strip()

    if "parter" in text:
        return 0

    match = re.search(r"piętro\s*([0-9]+)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))

    return None


def normalize_url(href):
    if not href:
        return None
    if href.startswith("http"):
        return href
    return f"https://gratka.pl{href}"



# PARSOWANIE KARTY

async def parse_card(card, city, listing_page):
    href = await card.get_attribute("href")
    href = normalize_url(href)

    title_el = await card.query_selector('[data-cy="propertyCardTitle"]')
    location_el = await card.query_selector('[data-cy="propertyCardLocation"] span')
    price_el = await card.query_selector('[data-cy="cardPropertyOfferPrice"]')
    info_el = await card.query_selector('[data-cy="propertyCardInfo"]')
    desc_el = await card.query_selector('.property-card__property-description .description')

    title = await text_or_none(title_el)
    location = await text_or_none(location_el)
    price_text = await text_or_none(price_el)
    info_text = await text_or_none(info_el)
    description = await text_or_none(desc_el)

    return {
        "city": city,
        "listing_page": listing_page,
        "offer_url": href,
        "title": title,
        "location_raw": location,
        "price_raw": price_text,
        "price": parse_price(price_text),
        "price_per_m2": parse_price_per_m2(price_text),
        "info_raw": info_text,
        "area_m2": parse_area(info_text),
        "rooms": parse_rooms(info_text),
        "floor": parse_floor(info_text),
        "description": description,
        "scrape_date": datetime.now().isoformat(),
    }



# SCRAPOWANIE JEDNEGO MIASTA

async def scrape_city(page, city, base_url):
    results = []

    for page_num in range(1, MAX_PAGES_PER_CITY + 1):
        if page_num == 1:
            url = f"{base_url}"
        else:
            url = f"{base_url}?page={page_num}"
        print(f"[{city}] strona {page_num}: {url}")

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2500)
            await accept_cookies(page)

            cards = await page.query_selector_all('a[data-cy="propertyUrl"]')
            print(f"  znaleziono kart: {len(cards)}")

            if len(cards) == 0:
                print("  brak kart — możliwe, że selektor się zmienił albo strona się nie załadowała")
                await random_delay()
                continue

            for card in cards:
                try:
                    row = await parse_card(card, city, page_num)
                    results.append(row)
                except Exception as e:
                    print(f"  [BŁĄD KARTY] {e}")

            await random_delay()

        except PlaywrightTimeout:
            print(f"  [TIMEOUT] {url}")
        except Exception as e:
            print(f"  [ERROR] {url} -> {e}")

    return results



# GŁÓWNA FUNKCJA

async def main():
    all_rows = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 1000},
            locale="pl-PL",
        )
        page = await context.new_page()

        for city, base_url in CITIES.items():
            print(f"\n{'=' * 60}")
            print(f"SCRAPUJĘ MIASTO: {city.upper()}")
            print(f"{'=' * 60}")

            city_rows = await scrape_city(page, city, base_url)
            all_rows.extend(city_rows)

            df_partial = pd.DataFrame(all_rows)
            if not df_partial.empty:
                df_partial = df_partial.drop_duplicates(subset=["offer_url"])
                df_partial.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
                print(f"Zapis częściowy: {len(df_partial)} rekordów")

        await browser.close()

    df = pd.DataFrame(all_rows)

    if df.empty:
        print("Brak danych.")
        return

    # deduplikacja
    df = df.drop_duplicates(subset=["offer_url"])

    # podstawowa filtracja jakości
    df = df[df["price"].notna()]
    df = df[df["area_m2"].notna()]
    df = df[(df["price"] > 50000) & (df["price"] < 20000000)]
    df = df[(df["area_m2"] > 10) & (df["area_m2"] < 400)]

    # jeśli nie złapało ceny za m2, policz
    df["price_per_m2"] = df["price_per_m2"].fillna(df["price"] / df["area_m2"])

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\nGotowe. Zapisano {len(df)} rekordów do {OUTPUT_FILE}")
    print(df.head())
    print(df.dtypes)


if __name__ == "__main__":
    asyncio.run(main())