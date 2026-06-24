"""
Tests for scrapers/merger.py

The module under test is expected to expose:
  - merge(bbva_list: list[dict], santander_list: list[dict]) -> list[dict]

The merge function must:
  - Combine both lists into a unified list
  - Deduplicate by (bank, id)
  - Preserve all required unified schema fields
  - Assign canonical_category from taxonomy if not already set
  - Handle empty inputs gracefully
  - Return results sorted by discount_pct descending
"""

import pytest

MERGER_MODULE = "scrapers.merger"

REQUIRED_UNIFIED_FIELDS = {
    "id", "bank", "canonical_category", "store_name", "title",
    "description", "discount_pct", "installments", "valid_from",
    "valid_until", "days_active", "card_types", "url", "image_url", "raw",
}


def _make_discount(bank: str, id_: str, canonical_category: str, discount_pct: int) -> dict:
    return {
        "id": id_,
        "bank": bank,
        "canonical_category": canonical_category,
        "store_name": f"Store {id_}",
        "title": f"Promo {id_}",
        "description": f"Description for {id_}",
        "discount_pct": discount_pct,
        "installments": 0,
        "valid_from": "2026-06-01",
        "valid_until": "2026-06-30",
        "days_active": [-1],
        "card_types": ["credito_visa"],
        "url": None,
        "image_url": None,
        "raw": {},
    }


def _import_or_skip():
    try:
        import importlib
        return importlib.import_module(MERGER_MODULE)
    except ModuleNotFoundError:
        pytest.skip(f"Module '{MERGER_MODULE}' not yet implemented.")


# ===========================================================================
# 1. Deduplication by bank and id
# ===========================================================================

def test_merge_deduplicates_by_bank_and_id():
    """Duplicate entries with same (bank, id) appear only once in output."""
    merger = _import_or_skip()
    d1 = _make_discount("bbva", "bbva-100", "moda", 20)
    d2 = _make_discount("bbva", "bbva-100", "moda", 20)  # duplicate
    d3 = _make_discount("santander", "sant-200", "supermercados", 30)

    result = merger.merge([d1, d2], [d3])

    ids = [(r["bank"], r["id"]) for r in result]
    assert len(ids) == len(set(ids)), "Duplicates found in merge output."
    assert len(result) == 2


# ===========================================================================
# 2. All required fields preserved in merged output
# ===========================================================================

def test_merge_preserves_all_required_fields():
    """Every item in the merged output contains all required unified schema fields."""
    merger = _import_or_skip()
    bbva = [_make_discount("bbva", "bbva-1", "moda", 10)]
    santander = [_make_discount("santander", "sant-1", "supermercados", 25)]

    result = merger.merge(bbva, santander)

    for item in result:
        missing = REQUIRED_UNIFIED_FIELDS - set(item.keys())
        assert missing == set(), f"Item '{item.get('id')}' is missing fields: {missing}"


# ===========================================================================
# 3. Canonical category assigned from taxonomy
# ===========================================================================

def test_merge_assigns_canonical_category():
    """Merged items have a non-empty canonical_category string."""
    merger = _import_or_skip()
    bbva = [_make_discount("bbva", "bbva-10", "moda", 15)]
    santander = [_make_discount("santander", "sant-10", "gastronomia", 5)]

    result = merger.merge(bbva, santander)

    for item in result:
        assert item.get("canonical_category"), f"Empty canonical_category in item '{item.get('id')}'"


# ===========================================================================
# 4. Handles empty BBVA input
# ===========================================================================

def test_merge_handles_empty_bbva_input():
    """merge() with empty BBVA list returns only Santander items without error."""
    merger = _import_or_skip()
    santander = [_make_discount("santander", "sant-1", "supermercados", 30)]

    result = merger.merge([], santander)

    assert len(result) == 1
    assert result[0]["bank"] == "santander"


# ===========================================================================
# 5. Handles empty Santander input
# ===========================================================================

def test_merge_handles_empty_santander_input():
    """merge() with empty Santander list returns only BBVA items without error."""
    merger = _import_or_skip()
    bbva = [_make_discount("bbva", "bbva-1", "moda", 20)]

    result = merger.merge(bbva, [])

    assert len(result) == 1
    assert result[0]["bank"] == "bbva"


# ===========================================================================
# 6. Output sorted by discount_pct descending
# ===========================================================================

def test_output_sorted_by_discount_desc():
    """merge() output is sorted by discount_pct from highest to lowest."""
    merger = _import_or_skip()
    bbva = [
        _make_discount("bbva", "bbva-1", "moda", 10),
        _make_discount("bbva", "bbva-2", "moda", 30),
    ]
    santander = [
        _make_discount("santander", "sant-1", "supermercados", 20),
    ]

    result = merger.merge(bbva, santander)

    discounts = [r["discount_pct"] for r in result]
    assert discounts == sorted(discounts, reverse=True), \
        f"Output not sorted desc by discount_pct: {discounts}"
