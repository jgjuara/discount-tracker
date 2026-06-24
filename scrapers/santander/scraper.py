import argparse
import json
import os
import time
import requests

from scrapers.santander.normalizer import normalize_brand
from scrapers.taxonomy import SANTANDER_CAT_MAP

class SantanderScraperError(Exception):
    pass

class SantanderScraper:
    STA_CATEGORIES = [
        "AUT", "DEP", "DIN", "EDU", "ESP", "FAR",
        "GAS", "HOG", "IND", "JUG", "LIB", "PELU",
        "PER", "SUP", "VAR", "VIA",
    ]
    EXC_CATEGORIES = ["CPE", "MOD", "SEC", "SMI", "SOR"]

    def _request(self, url, params=None, timeout=15):
        retries = 3
        backoff = 1
        for attempt in range(retries):
            try:
                res = requests.get(url, params=params, timeout=timeout)
                if res.status_code == 429:
                    time.sleep(60)
                    continue
                elif res.status_code == 503:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                elif res.status_code != 200:
                    raise SantanderScraperError(f"HTTP {res.status_code} error")
                return res
            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt == retries - 1:
                    raise SantanderScraperError(f"Request failed: {e}")
                time.sleep(backoff)
                backoff *= 2
        raise SantanderScraperError("Max retries exceeded")

    def fetch_categories(self, type_: str = "STA") -> list[str]:
        url = "https://www.santander.com.ar/bff-benefits/categories"
        res = self._request(url, params={"type": type_})
        try:
            cats = res.json().get("categories", [])
            return [c["code"] for c in cats if "code" in c]
        except ValueError:
            raise SantanderScraperError("Invalid JSON response from categories endpoint")

    def fetch_brands_page(self, category=None, exclusive=None, page=1, limit=50) -> list[dict]:
        url = "https://www.santander.com.ar/bff-benefits/brands"
        params = {"page": page, "limit": limit}
        if category is not None:
            params["categories"] = category
        if exclusive is not None:
            params["exclusive"] = exclusive
        
        res = self._request(url, params=params)
        try:
            return res.json().get("brands", [])
        except ValueError:
            raise SantanderScraperError("Invalid JSON response from brands endpoint")

    def fetch_brand_detail(self, brand_id: int) -> dict:
        url = f"https://www.santander.com.ar/bff-benefits/brands/{brand_id}"
        res = self._request(url)
        try:
            return res.json()
        except ValueError:
            raise SantanderScraperError("Invalid JSON response from brand detail endpoint")

    def fetch_all(self) -> list[dict]:
        all_normalized = []
        seen_publications = set()

        # 1. Fetch STA categories
        try:
            sta_codes = self.fetch_categories(type_="STA")
        except Exception as e:
            print(f"Warning: failed to fetch STA categories: {e}. Using fallback.")
            sta_codes = self.STA_CATEGORIES

        # 2. Iterate STA categories
        for cat in sta_codes:
            canonical_cat = SANTANDER_CAT_MAP.get(cat, "bazar")
            page = 1
            while True:
                brands = self.fetch_brands_page(category=cat, page=page, limit=50)
                if not brands:
                    break
                for brand in brands:
                    brand_id = brand.get("id")
                    brand_name = brand.get("name")
                    if not brand_id:
                        continue
                    try:
                        detail = self.fetch_brand_detail(brand_id)
                        pubs = detail.get("publications", [])
                        for pub in pubs:
                            pub_id = pub.get("id")
                            uniq_key = (brand_id, pub_id)
                            if uniq_key not in seen_publications:
                                seen_publications.add(uniq_key)
                                normalized = normalize_brand(pub, brand_name, canonical_cat)
                                all_normalized.append(normalized)
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"Error fetching brand detail {brand_id}: {e}")
                page += 1

        # 3. Fetch EXC categories
        try:
            exc_codes = self.fetch_categories(type_="EXC")
        except Exception as e:
            print(f"Warning: failed to fetch EXC categories: {e}. Using fallback.")
            exc_codes = self.EXC_CATEGORIES

        # 4. Iterate EXC categories
        for cat in exc_codes:
            canonical_cat = SANTANDER_CAT_MAP.get(cat, "cuidado_personal")
            page = 1
            while True:
                brands = self.fetch_brands_page(exclusive=cat, page=page, limit=50)
                if not brands:
                    break
                for brand in brands:
                    brand_id = brand.get("id")
                    brand_name = brand.get("name")
                    if not brand_id:
                        continue
                    try:
                        detail = self.fetch_brand_detail(brand_id)
                        pubs = detail.get("publications", [])
                        for pub in pubs:
                            pub_id = pub.get("id")
                            uniq_key = (brand_id, pub_id)
                            if uniq_key not in seen_publications:
                                seen_publications.add(uniq_key)
                                normalized = normalize_brand(pub, brand_name, canonical_cat)
                                all_normalized.append(normalized)
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"Error fetching brand detail {brand_id}: {e}")
                page += 1

        return all_normalized

def main():
    parser = argparse.ArgumentParser(description="Santander Scraper CLI")
    parser.add_argument("--output", required=True, help="Path to save the JSON output")
    args = parser.parse_args()

    scraper = SantanderScraper()
    print("Scraping Santander benefits...")
    all_normalized_promos = scraper.fetch_all()
    print(f"Fetched {len(all_normalized_promos)} normalized Santander promos.")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_normalized_promos, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_normalized_promos)} normalized Santander promos to {args.output}")

if __name__ == "__main__":
    main()
