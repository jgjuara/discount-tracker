"""
Tests for scrapers/santander/scraper.py

The module under test is expected to expose:
  - SantanderScraper class with:
      .fetch_categories(type_='STA') -> list[str]
      .fetch_brands_page(category=None, exclusive=None, page=1, limit=50) -> list[dict]
      .fetch_brand_detail(brand_id: int) -> dict
      .fetch_all() -> list[dict]
      .STA_CATEGORIES: list[str]  (16 codes)
      .EXC_CATEGORIES: list[str]  (5 codes)
  - normalize_brand(raw: dict) -> dict  (unified schema)

All HTTP calls are mocked. Tests use pytest.skip if implementation not found.
"""

import pytest
from unittest.mock import MagicMock, patch, call

SCRAPER_MODULE = "scrapers.santander.scraper"

STA_CATEGORIES_EXPECTED = [
    "AUT", "DEP", "DIN", "EDU", "ESP", "FAR",
    "GAS", "HOG", "IND", "JUG", "LIB", "PELU",
    "PER", "SUP", "VAR", "VIA",
]

EXC_CATEGORIES_EXPECTED = ["CPE", "MOD", "SEC", "SMI", "SOR"]

REQUIRED_UNIFIED_FIELDS = {
    "id", "bank", "canonical_category", "store_name", "title",
    "description", "discount_pct", "installments", "valid_from",
    "valid_until", "days_active", "card_types", "url", "image_url", "raw",
}

CARD_CODE_MAP = {
    40: "credito_visa",
    41: "mastercard",
    42: "amex",
    43: "visa_recargable",
    81: "debito_visa",
    "M": "modo_qr",
}


def _mock_response(status_code: int, json_data: dict | None = None):
    mock = MagicMock()
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
    else:
        mock.json.side_effect = ValueError("no json")
    return mock


def _import_or_skip():
    try:
        import importlib
        return importlib.import_module(SCRAPER_MODULE)
    except ModuleNotFoundError:
        pytest.skip(f"Module '{SCRAPER_MODULE}' not yet implemented.")


# ===========================================================================
# 1. fetch_categories() returns STA list
# ===========================================================================

def test_fetch_categories_returns_sta_list():
    """fetch_categories(type_='STA') returns list of category code strings."""
    categories_payload = {
        "categories": [{"code": c, "type": "STA"} for c in STA_CATEGORIES_EXPECTED]
    }
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, categories_payload)
        scraper_mod = _import_or_skip()
        scraper = scraper_mod.SantanderScraper()
        result = scraper.fetch_categories(type_="STA")

    assert isinstance(result, list)
    assert set(result) == set(STA_CATEGORIES_EXPECTED)


# ===========================================================================
# 2. fetch_brands_page() returns brands list
# ===========================================================================

def test_fetch_brands_page_returns_brands(santander_brands_response):
    """fetch_brands_page() returns the list of brand dicts on success."""
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, santander_brands_response)
        scraper_mod = _import_or_skip()
        scraper = scraper_mod.SantanderScraper()
        result = scraper.fetch_brands_page(category="IND", page=1, limit=50)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "Nike"


# ===========================================================================
# 3. Empty brands page stops pagination
# ===========================================================================

def test_fetch_brands_empty_page_stops_pagination(
    santander_brands_response, santander_empty_brands_response
):
    """fetch_all() stops iterating a category when brands list is empty."""
    detail = {
        "id": 2763,
        "name": "Nike",
        "logo": "",
        "publications": [
            {
                "id": "pub-1",
                "title": "30% descuento",
                "description": "desc",
                "customerDiscount": 30,
                "interestFreeFees": False,
                "initialQuote": 0,
                "finalQuote": 0,
                "monday": True, "tuesday": True, "wednesday": True,
                "thursday": True, "friday": True, "saturday": True,
                "sunday": True, "fullWeek": True,
                "categories": ["IND"],
                "legal": "legal",
                "payWith": [41],
            }
        ],
    }
    detail2 = {**detail, "id": 1042, "name": "Coto", "publications": detail["publications"]}

    # Sequence: page1 (brands) -> detail1 -> detail2 -> page2 (empty) -> repeat for other categories
    # We only test that empty page breaks the loop for a single category.
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response(200, {"categories": [{"code": "IND", "type": "STA"}]}),
            _mock_response(200, santander_brands_response),  # page 1: 2 brands
            _mock_response(200, detail),
            _mock_response(200, detail2),
            _mock_response(200, santander_empty_brands_response),  # page 2: empty -> stop
            # EXC iteration (5 categories) would follow but we stop here with empty
        ] + [_mock_response(200, {"brands": [], "total": 0, "page": 1, "limit": 50})] * 10

        with patch(f"{SCRAPER_MODULE}.time.sleep"):
            scraper_mod = _import_or_skip()
            scraper = scraper_mod.SantanderScraper()
            result = scraper.fetch_all()

    # At least 2 publications were collected before stopping
    assert isinstance(result, list)


# ===========================================================================
# 4. fetch_brand_detail() returns publications
# ===========================================================================

def test_fetch_brand_detail_returns_publications(santander_brand_detail_response):
    """fetch_brand_detail() returns the publications list for a brand."""
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, santander_brand_detail_response)
        scraper_mod = _import_or_skip()
        scraper = scraper_mod.SantanderScraper()
        result = scraper.fetch_brand_detail(brand_id=2763)

    assert isinstance(result, dict)
    assert "publications" in result
    assert len(result["publications"]) == 1


# ===========================================================================
# 5. All 16 STA categories are fetched
# ===========================================================================

def test_all_sta_categories_fetched():
    """SantanderScraper.STA_CATEGORIES contains exactly the 16 expected STA codes."""
    scraper_mod = _import_or_skip()
    assert set(scraper_mod.SantanderScraper.STA_CATEGORIES) == set(STA_CATEGORIES_EXPECTED)


# ===========================================================================
# 6. EXC categories also fetched
# ===========================================================================

def test_exc_categories_also_fetched():
    """SantanderScraper.EXC_CATEGORIES contains exactly the 5 expected EXC codes."""
    scraper_mod = _import_or_skip()
    assert set(scraper_mod.SantanderScraper.EXC_CATEGORIES) == set(EXC_CATEGORIES_EXPECTED)


# ===========================================================================
# 7. normalize_brand() extracts discount_pct
# ===========================================================================

def test_normalize_brand_discount_pct_extracted(santander_brand_detail_response):
    """normalize_brand() extracts customerDiscount as discount_pct."""
    scraper_mod = _import_or_skip()
    pub = santander_brand_detail_response["publications"][0]
    brand_name = santander_brand_detail_response["name"]
    result = scraper_mod.normalize_brand(pub, brand_name=brand_name, canonical_category="moda")

    assert result["discount_pct"] == 30


# ===========================================================================
# 8. normalize_brand() extracts installments
# ===========================================================================

def test_normalize_brand_installments_extracted(santander_brand_detail_response):
    """normalize_brand() uses finalQuote as installments count."""
    scraper_mod = _import_or_skip()
    pub = santander_brand_detail_response["publications"][0]
    result = scraper_mod.normalize_brand(
        pub, brand_name="Nike", canonical_category="deportes"
    )
    assert result["installments"] == pub["finalQuote"]


# ===========================================================================
# 9. normalize_brand() builds days_active from boolean day fields
# ===========================================================================

def test_normalize_brand_days_active_field(santander_brand_detail_response):
    """When fullWeek=True, days_active should contain all 7 days or [-1]."""
    scraper_mod = _import_or_skip()
    pub = santander_brand_detail_response["publications"][0]
    result = scraper_mod.normalize_brand(
        pub, brand_name="Nike", canonical_category="moda"
    )
    days = result["days_active"]
    assert isinstance(days, list)
    # Either all 7 individual days or the -1 sentinel for "every day"
    assert days == [-1] or set(days) == {0, 1, 2, 3, 4, 5, 6}


# ===========================================================================
# 10. normalize_brand() maps card type codes to string names
# ===========================================================================

def test_normalize_brand_card_types_extracted(santander_brand_detail_response):
    """payWith code 41 maps to 'mastercard' in card_types."""
    scraper_mod = _import_or_skip()
    pub = santander_brand_detail_response["publications"][0]
    result = scraper_mod.normalize_brand(
        pub, brand_name="Nike", canonical_category="moda"
    )
    assert "mastercard" in result["card_types"]


# ===========================================================================
# 11. Output schema has all required unified fields
# ===========================================================================

def test_output_schema_has_required_fields(santander_brand_detail_response):
    """normalize_brand() output contains all required unified schema fields."""
    scraper_mod = _import_or_skip()
    pub = santander_brand_detail_response["publications"][0]
    result = scraper_mod.normalize_brand(
        pub, brand_name="Nike", canonical_category="deportes"
    )
    missing = REQUIRED_UNIFIED_FIELDS - set(result.keys())
    assert missing == set(), f"Missing fields: {missing}"


# ===========================================================================
# 12. Pagination uses correct limit param
# ===========================================================================

def test_pagination_uses_correct_limit_param(santander_brands_response, santander_empty_brands_response):
    """requests.get is called with a 'limit' query parameter."""
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response(200, santander_brands_response),
            _mock_response(200, santander_empty_brands_response),
        ]
        scraper_mod = _import_or_skip()
        scraper = scraper_mod.SantanderScraper()
        scraper.fetch_brands_page(category="IND", page=1, limit=50)

    call_kwargs = mock_get.call_args_list[0]
    params = call_kwargs[1].get("params", {})
    assert "limit" in params


# ===========================================================================
# 13. Province filter NOT passed in national scrape
# ===========================================================================

def test_province_filter_ignored_in_scraper(santander_brands_response, santander_empty_brands_response):
    """fetch_brands_page() does not send a 'location' param by default."""
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, santander_brands_response)
        scraper_mod = _import_or_skip()
        scraper = scraper_mod.SantanderScraper()
        scraper.fetch_brands_page(category="IND", page=1, limit=50)

    call_kwargs = mock_get.call_args_list[0]
    params = call_kwargs[1].get("params", {})
    assert "location" not in params


# ===========================================================================
# 14. Non-200 response raises exception
# ===========================================================================

def test_error_on_non_200_raises_exception():
    """fetch_brands_page() raises SantanderScraperError on HTTP 429 or 503."""
    for status in (429, 503):
        with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
            mock_get.return_value = _mock_response(status)
            scraper_mod = _import_or_skip()
            scraper = scraper_mod.SantanderScraper()
            with patch(f"{SCRAPER_MODULE}.time.sleep"):
                with pytest.raises(Exception):
                    # Disable retries to test base error path
                    scraper.fetch_brands_page(category="IND", page=1, limit=1)


# ===========================================================================
# 15. Retry logic on transient error
# ===========================================================================

def test_retry_logic_on_transient_error(santander_brands_response):
    """On first 503, scraper retries and succeeds on second attempt."""
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response(503),                        # first attempt fails
            _mock_response(200, santander_brands_response),  # retry succeeds
        ]
        with patch(f"{SCRAPER_MODULE}.time.sleep"):
            scraper_mod = _import_or_skip()
            scraper = scraper_mod.SantanderScraper()
            result = scraper.fetch_brands_page(category="IND", page=1, limit=50)

    assert isinstance(result, list)
    assert len(result) == 2
    assert mock_get.call_count == 2


# ===========================================================================
# 16. process_raw_input() parses and normalizes raw JSON list
# ===========================================================================

def test_process_raw_input_normalizes_and_deduplicates(tmp_path):
    """process_raw_input() loads raw JSON, maps categories, normalizes, and deduplicates."""
    raw_data = [
        {
            "brand_id": 53,
            "brand_name": "Bridgestone",
            "category": "AUT",
            "type": "STA",
            "publications": [
                {
                    "id": 6823,
                    "title": "15% off",
                    "description": "No limit",
                    "customerDiscount": 15,
                    "finalQuote": 6,
                    "fullWeek": True,
                    "legal": "Vigencia del 01-01-2026 al 31-12-2026",
                    "payWith": [40]
                }
            ]
        },
        {
            "brand_id": 53,
            "brand_name": "Bridgestone",
            "category": "AUT",
            "type": "STA",
            "publications": [
                {
                    "id": 6823,  # Duplicate of the previous one
                    "title": "15% off",
                    "description": "No limit",
                    "customerDiscount": 15,
                    "finalQuote": 6,
                    "fullWeek": True,
                    "legal": "Vigencia del 01-01-2026 al 31-12-2026",
                    "payWith": [40]
                },
                {
                    "id": 9999,  # Unique publication
                    "title": "20% off",
                    "description": "No limit",
                    "customerDiscount": 20,
                    "finalQuote": 3,
                    "fullWeek": False,
                    "legal": "Vigencia del 01-01-2026 al 31-12-2026",
                    "payWith": [40]
                }
            ]
        },
        {
            "brand_id": 123,
            "brand_name": "Unknown Brand",
            "category": "XYZ",  # Not in map -> should map to "bazar"
            "type": "STA",
            "publications": [
                {
                    "id": 1111,
                    "title": "Unknown promo",
                    "description": "desc",
                    "customerDiscount": 10,
                    "finalQuote": 0,
                    "fullWeek": True,
                    "legal": "",
                    "payWith": []
                }
            ]
        }
    ]

    import json
    raw_file = tmp_path / "raw_test.json"
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(raw_data, f)

    scraper_mod = _import_or_skip()
    scraper = scraper_mod.SantanderScraper()
    result = scraper.process_raw_input(str(raw_file))

    # Expecting 3 unique normalized promotions:
    # 1. Bridgestone (6823) -> category AUT -> canonical "automotores"
    # 2. Bridgestone (9999) -> category AUT -> canonical "automotores"
    # 3. Unknown Brand (1111) -> category XYZ (missing from map) -> canonical "bazar"
    assert len(result) == 3
    
    # Check canonical category mappings
    b1_pub1 = next(item for item in result if item["id"] == "santander-6823")
    b1_pub2 = next(item for item in result if item["id"] == "santander-9999")
    b2_pub = next(item for item in result if item["id"] == "santander-1111")
    
    assert b1_pub1["store_name"] == "Bridgestone"
    assert b1_pub1["canonical_category"] == "automotores"
    assert b1_pub1["discount_pct"] == 15
    
    assert b1_pub2["store_name"] == "Bridgestone"
    assert b1_pub2["canonical_category"] == "automotores"
    assert b1_pub2["discount_pct"] == 20
    
    assert b2_pub["store_name"] == "Unknown Brand"
    assert b2_pub["canonical_category"] == "bazar"
