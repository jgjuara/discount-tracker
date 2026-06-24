import argparse
import json
import os
import time
import requests

from scrapers.bbva.normalizer import (
    normalize_promo,
    extract_discount_and_cuotas,
    classify_promotion,
)

class BBVAScraperError(Exception):
    pass

class BBVAScraper:
    HEADERS = {
        "accept": "*/*",
        "accept-language": "es-AR,es-US;q=0.9,es;q=0.8",
        "origin": "https://www.bbva.com.ar",
        "referer": "https://www.bbva.com.ar/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    }

    def fetch_page(self, rubro_id: int, pager: int) -> list[dict]:
        params = {"pager": pager, "rubros": rubro_id}
        retries = 3
        backoff = 1
        for attempt in range(retries):
            try:
                res = requests.get(
                    "https://go.bbva.com.ar/willgo/fgo/API/v3/communications",
                    headers=self.HEADERS,
                    params=params,
                    timeout=10,
                )
                if res.status_code == 500:
                    raise BBVAScraperError(f"HTTP 500 error on pager={pager}, rubro={rubro_id}")
                elif res.status_code != 200:
                    raise BBVAScraperError(f"HTTP {res.status_code} error")
                
                try:
                    return res.json().get("data", [])
                except ValueError:
                    raise BBVAScraperError("Invalid JSON response from BBVA API")
            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt == retries - 1:
                    raise BBVAScraperError(f"Request failed after {retries} attempts: {e}")
                time.sleep(backoff)
                backoff *= 2

    def fetch_all(self, rubro_id: int) -> list[dict]:
        all_promos = []
        pager = 0
        while True:
            try:
                promos = self.fetch_page(rubro_id, pager)
                if not promos:
                    break
                all_promos.extend(promos)
                pager += 1
                time.sleep(0.3)
            except BBVAScraperError as e:
                print(f"Warning: BBVAScraperError on pager={pager}, rubro={rubro_id}: {e}. Stopping pagination.")
                break
        return all_promos

def main():
    parser = argparse.ArgumentParser(description="BBVA Scraper CLI")
    parser.add_argument("--output", required=True, help="Path to save the JSON output")
    args = parser.parse_args()

    active_rubros = [3, 4, 8, 13, 26, 170, 173, 174, 175, 184, 192, 195]
    scraper = BBVAScraper()
    all_normalized_promos = []

    for rubro_id in active_rubros:
        print(f"Scraping BBVA rubro {rubro_id}...")
        raw_promos = scraper.fetch_all(rubro_id)
        print(f"Fetched {len(raw_promos)} raw promos for rubro {rubro_id}.")
        for raw in raw_promos:
            normalized = normalize_promo(raw, rubro_id)
            all_normalized_promos.append(normalized)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_normalized_promos, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_normalized_promos)} normalized BBVA promos to {args.output}")

if __name__ == "__main__":
    main()
