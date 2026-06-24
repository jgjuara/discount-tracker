import re

CARD_CODE_MAP = {
    40: "credito_visa",
    41: "mastercard",
    42: "amex",
    43: "visa_recargable",
    81: "debito_visa",
    "M": "modo_qr",
}

def parse_dates_from_legal(legal_text):
    if not legal_text:
        return None, None
    matches = re.findall(r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', legal_text)
    if len(matches) >= 2:
        d1, m1, y1 = matches[0]
        d2, m2, y2 = matches[1]
        valid_from = f"{y1}-{int(m1):02d}-{int(d1):02d}"
        valid_until = f"{y2}-{int(m2):02d}-{int(d2):02d}"
        return valid_from, valid_until
    elif len(matches) == 1:
        d1, m1, y1 = matches[0]
        return f"{y1}-{int(m1):02d}-{int(d1):02d}", None
    return None, None

def normalize_brand(pub: dict, brand_name: str, canonical_category: str) -> dict:
    discount_pct = int(pub.get("customerDiscount") or 0)
    installments = int(pub.get("finalQuote") or 0)
    
    # Parse valid_from and valid_until from 'legal' field
    legal = pub.get("legal", "")
    valid_from, valid_until = parse_dates_from_legal(legal)

    # Days active
    days_active = []
    if pub.get("fullWeek"):
        days_active = [-1]
    else:
        day_mapping = [
            ("sunday", 0),
            ("monday", 1),
            ("tuesday", 2),
            ("wednesday", 3),
            ("thursday", 4),
            ("friday", 5),
            ("saturday", 6),
        ]
        for field, day_idx in day_mapping:
            if pub.get(field):
                days_active.append(day_idx)
        if not days_active:
            days_active = [-1]
        else:
            days_active = sorted(days_active)

    # Card types
    pay_with = pub.get("payWith") or []
    card_types = []
    for code in pay_with:
        mapped = CARD_CODE_MAP.get(code)
        if not mapped:
            mapped = CARD_CODE_MAP.get(str(code))
        if not mapped:
            try:
                mapped = CARD_CODE_MAP.get(int(code))
            except ValueError:
                pass
        if mapped:
            card_types.append(mapped)

    return {
        "id": f"santander-{pub.get('id')}",
        "bank": "santander",
        "canonical_category": canonical_category,
        "store_name": brand_name,
        "title": pub.get("title") or "",
        "description": pub.get("description") or "",
        "discount_pct": discount_pct,
        "installments": installments,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "days_active": days_active,
        "card_types": card_types,
        "url": None,
        "image_url": None,
        "raw": pub,
    }
