"""
Tests for scrapers/bbva/scraper.py

The module under test is expected to expose:
  - BBVAScraper class with:
      .fetch_page(rubro_id, pager) -> list[dict]
      .fetch_all(rubro_id) -> list[dict]
      .HEADERS: dict
  - normalize_promo(raw: dict) -> dict  (unified schema)
  - extract_discount_and_cuotas(cabecera, subcabecera) -> tuple[int, int]
  - classify_promotion(cabecera, subcabecera) -> tuple[bool, bool]

All HTTP calls are mocked via unittest.mock.patch so no real network traffic
is generated. Tests are designed to pass once the implementation exists.
"""

import sys
import types
import pytest
from unittest.mock import MagicMock, patch, call

# ---------------------------------------------------------------------------
# Module path where the real implementation will live.
# Tests use patch() against these paths so they work even before the
# implementation exists (the module is created as a MagicMock stub here).
# ---------------------------------------------------------------------------
SCRAPER_MODULE = "scrapers.bbva.scraper"
NORMALIZER_MODULE = "scrapers.bbva.normalizer"

# ---------------------------------------------------------------------------
# Helper: build a mock response object
# ---------------------------------------------------------------------------

def _mock_response(status_code: int, json_data: dict | None = None):
    mock = MagicMock()
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
    else:
        mock.json.side_effect = ValueError("no json")
    return mock


# ===========================================================================
# 1. fetch_page() — success path
# ===========================================================================

def test_fetch_page_returns_promos_on_success(bbva_list_response):
    """fetch_page() returns the list of promos when the API responds 200."""
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, bbva_list_response)
        # Import lazily so patching takes effect
        scraper_mod = _import_or_skip()
        scraper = scraper_mod.BBVAScraper()
        result = scraper.fetch_page(rubro_id=170, pager=0)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == "85443"


# ===========================================================================
# 2. fetch_page() — out-of-range pager returns empty list
# ===========================================================================

def test_fetch_page_returns_empty_on_out_of_range_pager(bbva_empty_list_response):
    """When pager is beyond last page, API returns 200 with data=[]. fetch_page() returns []."""
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, bbva_empty_list_response)
        scraper_mod = _import_or_skip()
        scraper = scraper_mod.BBVAScraper()
        result = scraper.fetch_page(rubro_id=170, pager=999)

    assert result == []


# ===========================================================================
# 3. fetch_page() — HTTP 500 raises exception
# ===========================================================================

def test_fetch_page_raises_on_500():
    """fetch_page() raises BBVAScraperError (or equivalent) on HTTP 500."""
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.return_value = _mock_response(500)
        scraper_mod = _import_or_skip()
        scraper = scraper_mod.BBVAScraper()
        with pytest.raises(Exception):
            scraper.fetch_page(rubro_id=170, pager=-1)


# ===========================================================================
# 4. fetch_all() — stops when data is empty
# ===========================================================================

def test_fetch_all_stops_when_data_empty(bbva_list_response, bbva_empty_list_response):
    """fetch_all() collects first page and stops on second empty page."""
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response(200, bbva_list_response),
            _mock_response(200, bbva_empty_list_response),
        ]
        with patch(f"{SCRAPER_MODULE}.time.sleep"):
            scraper_mod = _import_or_skip()
            scraper = scraper_mod.BBVAScraper()
            result = scraper.fetch_all(rubro_id=170)

    assert len(result) == 2  # only first page (2 items)


# ===========================================================================
# 5. fetch_all() — collects all pages
# ===========================================================================

def test_pagination_collects_all_pages(bbva_list_response, bbva_empty_list_response):
    """fetch_all() iterates through 3 pages of data, stops on 4th empty page."""
    resp_page = dict(bbva_list_response, message="Comunicaciones: 6   paginas: 3")
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response(200, resp_page),   # page 0: 2 items
            _mock_response(200, resp_page),   # page 1: 2 items
            _mock_response(200, resp_page),   # page 2: 2 items
            _mock_response(200, bbva_empty_list_response),  # page 3: stop
        ]
        with patch(f"{SCRAPER_MODULE}.time.sleep"):
            scraper_mod = _import_or_skip()
            scraper = scraper_mod.BBVAScraper()
            result = scraper.fetch_all(rubro_id=170)

    assert len(result) == 6  # 3 pages × 2 items


# ===========================================================================
# 6. Required headers sent in every request
# ===========================================================================

def test_headers_sent_in_request(bbva_list_response, bbva_empty_list_response):
    """requests.get is called with headers containing 'origin' and 'referer'."""
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response(200, bbva_list_response),
            _mock_response(200, bbva_empty_list_response),
        ]
        with patch(f"{SCRAPER_MODULE}.time.sleep"):
            scraper_mod = _import_or_skip()
            scraper = scraper_mod.BBVAScraper()
            scraper.fetch_all(rubro_id=170)

    call_kwargs = mock_get.call_args_list[0][1]
    headers = call_kwargs.get("headers", {})
    assert "origin" in headers
    assert "referer" in headers
    assert "bbva.com.ar" in headers["origin"]


# ===========================================================================
# 7-9. extract_discount_and_cuotas() unit tests
# ===========================================================================

def test_normalize_promo_discount_pct_extracted():
    """extract_discount_and_cuotas returns correct pct when cabecera has '30%'."""
    scraper_mod = _import_or_skip()
    pct, cuotas = scraper_mod.extract_discount_and_cuotas(
        "Nike 30% de reintegro", "30% reintegro con tarjeta BBVA"
    )
    assert pct == 30


def test_normalize_promo_cuotas_extracted():
    """extract_discount_and_cuotas returns correct cuotas count."""
    scraper_mod = _import_or_skip()
    pct, cuotas = scraper_mod.extract_discount_and_cuotas(
        "Zara 6 cuotas sin interés", "Hasta 6 cuotas"
    )
    assert cuotas == 6


def test_normalize_promo_no_discount_returns_zero():
    """Returns (0, 0) when no percent or cuotas info found."""
    scraper_mod = _import_or_skip()
    pct, cuotas = scraper_mod.extract_discount_and_cuotas(
        "Descuento especial en tienda", "Beneficio exclusivo para clientes"
    )
    assert pct == 0
    assert cuotas == 0


# ===========================================================================
# 10-13. classify_promotion() unit tests
# ===========================================================================

def test_classify_ropa_brand_detected():
    """Zara hombre -> is_ropa=True."""
    scraper_mod = _import_or_skip()
    is_ropa, is_calzado = scraper_mod.classify_promotion(
        "Zara hombre 20% descuento", "Descuento en indumentaria masculina"
    )
    assert is_ropa is True


def test_classify_calzado_brand_detected():
    """Nike zapatillas -> is_calzado=True."""
    scraper_mod = _import_or_skip()
    is_ropa, is_calzado = scraper_mod.classify_promotion(
        "Nike zapatillas 30%", "30% en calzado deportivo Nike"
    )
    assert is_calzado is True


def test_classify_general_brand_both_categories():
    """Nike alone (no keywords) -> both is_ropa=True and is_calzado=True."""
    scraper_mod = _import_or_skip()
    is_ropa, is_calzado = scraper_mod.classify_promotion(
        "Nike 6 cuotas sin interés", "Toda la tienda"
    )
    assert is_ropa is True
    assert is_calzado is True


def test_classify_unclassified_returns_false_false():
    """Unrelated text (e.g., optics store) returns (False, False)."""
    scraper_mod = _import_or_skip()
    is_ropa, is_calzado = scraper_mod.classify_promotion(
        "Óptica Central 10% descuento", "En lentes y marcos"
    )
    assert is_ropa is False
    assert is_calzado is False


# ===========================================================================
# 14. Output schema has all required unified fields
# ===========================================================================

REQUIRED_UNIFIED_FIELDS = {
    "id", "bank", "canonical_category", "store_name", "title",
    "description", "discount_pct", "installments", "valid_from",
    "valid_until", "days_active", "card_types", "url", "image_url", "raw",
}


def test_output_schema_has_required_fields(bbva_list_response):
    """normalize_promo() output dict contains all required unified schema fields."""
    scraper_mod = _import_or_skip()
    raw_promo = bbva_list_response["data"][0]
    result = scraper_mod.normalize_promo(raw_promo)
    missing = REQUIRED_UNIFIED_FIELDS - set(result.keys())
    assert missing == set(), f"Missing fields in normalized output: {missing}"


# ===========================================================================
# 15. Rate limit delay is applied between page requests
# ===========================================================================

def test_rate_limit_delay_applied(bbva_list_response, bbva_empty_list_response):
    """time.sleep() is called at least once between page requests."""
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response(200, bbva_list_response),
            _mock_response(200, bbva_empty_list_response),
        ]
        with patch(f"{SCRAPER_MODULE}.time.sleep") as mock_sleep:
            scraper_mod = _import_or_skip()
            scraper = scraper_mod.BBVAScraper()
            scraper.fetch_all(rubro_id=170)

    assert mock_sleep.call_count >= 1


# ===========================================================================
# 16. Pagination stops when pager >= total pages to prevent infinite loops
# ===========================================================================

def test_pagination_stops_when_pager_reaches_total_pages(bbva_list_response):
    """fetch_all() terminates immediately when pager reaches the number of total pages,
    even if the API repeatedly returns data.
    """
    resp_page_1 = dict(bbva_list_response, message="Comunicaciones: 2   paginas: 1")
    with patch(f"{SCRAPER_MODULE}.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response(200, resp_page_1),
            _mock_response(200, resp_page_1),
            _mock_response(200, resp_page_1),
        ]
        with patch(f"{SCRAPER_MODULE}.time.sleep"):
            scraper_mod = _import_or_skip()
            scraper = scraper_mod.BBVAScraper()
            result = scraper.fetch_all(rubro_id=13)

    assert len(result) == 2
    assert mock_get.call_count == 1


# ---------------------------------------------------------------------------
# Internal helper: lazy import that skips if implementation doesn't exist yet
# ---------------------------------------------------------------------------

def _import_or_skip():
    """
    Attempt to import the scraper module. Skip test if not yet implemented.
    This allows the test suite to be committed before the implementation.
    """
    try:
        import importlib
        return importlib.import_module(SCRAPER_MODULE)
    except ModuleNotFoundError:
        pytest.skip(f"Module '{SCRAPER_MODULE}' not yet implemented.")
