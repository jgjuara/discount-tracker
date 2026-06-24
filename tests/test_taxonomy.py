"""
Tests for scrapers/taxonomy.py

The module under test is expected to expose:
  - BBVA_RUBRO_MAP: dict[int, str]  — maps rubro ID -> canonical_key
  - SANTANDER_CAT_MAP: dict[str, str]  — maps STA code -> canonical_key
  - CANONICAL_CATEGORIES: list[dict]  — list of category definitions

Each category definition dict must have keys:
  canonical_key, display_name_es, icon_emoji, bbva_rubros, santander_categories
"""

import re
import pytest

TAXONOMY_MODULE = "scrapers.taxonomy"

BBVA_RUBROS_EXPECTED = {3, 4, 8, 13, 26, 170, 173, 174, 175, 184, 192, 195}

SANTANDER_STA_EXPECTED = {
    "AUT", "DEP", "DIN", "EDU", "ESP", "FAR",
    "GAS", "HOG", "IND", "JUG", "LIB", "PELU",
    "PER", "SUP", "VAR", "VIA",
}

SNAKE_CASE_RE = re.compile(r'^[a-z][a-z0-9_]*$')


def _import_or_skip():
    try:
        import importlib
        return importlib.import_module(TAXONOMY_MODULE)
    except ModuleNotFoundError:
        pytest.skip(f"Module '{TAXONOMY_MODULE}' not yet implemented.")


# ===========================================================================
# 1. All 12 BBVA rubros are mapped
# ===========================================================================

def test_all_bbva_rubros_mapped():
    """BBVA_RUBRO_MAP must contain all 12 known active rubro IDs."""
    tax = _import_or_skip()
    mapped_ids = set(tax.BBVA_RUBRO_MAP.keys())
    missing = BBVA_RUBROS_EXPECTED - mapped_ids
    assert missing == set(), f"Unmapped BBVA rubros: {missing}"


# ===========================================================================
# 2. All 16 Santander STA categories are mapped
# ===========================================================================

def test_all_santander_sta_categories_mapped():
    """SANTANDER_CAT_MAP must contain all 16 STA category codes."""
    tax = _import_or_skip()
    mapped_codes = set(tax.SANTANDER_CAT_MAP.keys())
    # Only check STA codes (EXC codes may optionally be present)
    missing = SANTANDER_STA_EXPECTED - mapped_codes
    assert missing == set(), f"Unmapped Santander STA categories: {missing}"


# ===========================================================================
# 3. No duplicate canonical keys
# ===========================================================================

def test_no_duplicate_canonical_keys():
    """CANONICAL_CATEGORIES must not contain duplicate canonical_key values."""
    tax = _import_or_skip()
    keys = [cat["canonical_key"] for cat in tax.CANONICAL_CATEGORIES]
    assert len(keys) == len(set(keys)), "Duplicate canonical_key entries found."


# ===========================================================================
# 4. All canonical keys are lowercase snake_case
# ===========================================================================

def test_canonical_key_format():
    """Every canonical_key must match the pattern [a-z][a-z0-9_]*."""
    tax = _import_or_skip()
    bad_keys = [
        cat["canonical_key"]
        for cat in tax.CANONICAL_CATEGORIES
        if not SNAKE_CASE_RE.match(cat["canonical_key"])
    ]
    assert bad_keys == [], f"Non-snake_case canonical keys: {bad_keys}"


# ===========================================================================
# 5. No empty display names
# ===========================================================================

def test_display_name_not_empty():
    """Every category entry must have a non-empty display_name_es string."""
    tax = _import_or_skip()
    empty = [
        cat["canonical_key"]
        for cat in tax.CANONICAL_CATEGORIES
        if not cat.get("display_name_es", "").strip()
    ]
    assert empty == [], f"Empty display_name_es for keys: {empty}"


# ===========================================================================
# 6. BBVA rubro 170 resolves to 'moda'
# ===========================================================================

def test_bbva_rubro_resolves_to_canonical():
    """BBVA rubro ID 170 (Moda/Accesorios) must map to canonical_key 'moda'."""
    tax = _import_or_skip()
    assert tax.BBVA_RUBRO_MAP[170] == "moda"


# ===========================================================================
# 7. Santander category IND resolves to 'moda'
# ===========================================================================

def test_santander_category_resolves_to_canonical():
    """Santander STA code 'IND' (Indumentaria) must map to canonical_key 'moda'."""
    tax = _import_or_skip()
    assert tax.SANTANDER_CAT_MAP["IND"] == "moda"


# ===========================================================================
# 8. Taxonomy can be imported as a Python module
# ===========================================================================

def test_taxonomy_loaded_from_module():
    """The taxonomy module must be importable and expose required attributes."""
    tax = _import_or_skip()
    assert hasattr(tax, "BBVA_RUBRO_MAP"), "Missing BBVA_RUBRO_MAP"
    assert hasattr(tax, "SANTANDER_CAT_MAP"), "Missing SANTANDER_CAT_MAP"
    assert hasattr(tax, "CANONICAL_CATEGORIES"), "Missing CANONICAL_CATEGORIES"
    assert isinstance(tax.CANONICAL_CATEGORIES, list)
    assert len(tax.CANONICAL_CATEGORIES) > 0
