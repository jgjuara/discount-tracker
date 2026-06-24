import argparse
import datetime
import json
import os
import re
from scrapers.taxonomy import SANTANDER_CAT_MAP, BBVA_RUBRO_MAP

REQUIRED_UNIFIED_FIELDS = {
    "id", "bank", "canonical_category", "store_name", "title",
    "description", "discount_pct", "installments", "valid_from",
    "valid_until", "days_active", "card_types", "url", "image_url", "raw",
}

def is_technology_brand_or_keyword(store_name, description):
    name_lower = (store_name or "").lower()
    desc_lower = (description or "").lower()
    
    tech_brands = [
        "fravega", "frávega", "musimundo", "samsung", "philips", "motorola", "lg", "sony",
        "xiaomi", "apple", "hp", "dell", "lenovo", "asus", "bgh", "noblex", "whirlpool"
    ]
    tech_keywords = [
        "electro", "tecnologia", "tecnología", "celular", "notebook", "televisión", "television",
        "tv", "computadora", "computacion", "computación", "tablet", "smart tv", "auriculares",
        "heladera", "lavarropas", "microondas", "aire acondicionado", "gopro", "consola",
        "playstation", "nintendo", "xbox"
    ]
    
    for brand in tech_brands:
        if re.search(r'\b' + re.escape(brand) + r'\b', name_lower) or re.search(r'\b' + re.escape(brand) + r'\b', desc_lower):
            return True
            
    for kw in tech_keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', name_lower) or re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
            return True
            
    return False

def merge(bbva_list: list[dict], santander_list: list[dict]) -> list[dict]:
    seen = set()
    merged = []
    
    for item in bbva_list + santander_list:
        bank = item.get("bank")
        item_id = item.get("id")
        key = (bank, item_id)
        if key not in seen:
            seen.add(key)
            item_copy = dict(item)
            
            # Ensure all required fields exist
            for field in REQUIRED_UNIFIED_FIELDS:
                if field not in item_copy:
                    item_copy[field] = None
            
            # Assign canonical category if not set or empty
            if not item_copy.get("canonical_category"):
                raw = item_copy.get("raw") or {}
                if bank == "santander" and "categories" in raw:
                    for cat in raw["categories"]:
                        if cat in SANTANDER_CAT_MAP:
                            item_copy["canonical_category"] = SANTANDER_CAT_MAP[cat]
                            break
                elif bank == "bbva" and "rubro_id" in raw:
                    item_copy["canonical_category"] = BBVA_RUBRO_MAP.get(raw["rubro_id"])
                
                if not item_copy.get("canonical_category"):
                    item_copy["canonical_category"] = "bazar"
            
            # Reclassify Santander VAR (bazar) to technology
            if bank == "santander" and item_copy.get("canonical_category") == "bazar":
                if is_technology_brand_or_keyword(item_copy.get("store_name"), item_copy.get("description")):
                    item_copy["canonical_category"] = "tecnologia"
            
            merged.append(item_copy)
            
    # Sort by discount_pct descending
    merged.sort(key=lambda x: x.get("discount_pct") or 0, reverse=True)
    return merged

def main():
    parser = argparse.ArgumentParser(description="Unified Merger CLI")
    parser.add_argument("--bbva", required=True, help="Path to BBVA JSON file")
    parser.add_argument("--santander", required=True, help="Path to Santander JSON file")
    parser.add_argument("--output", required=True, help="Path to save unified JSON output")
    args = parser.parse_args()

    bbva_list = []
    if os.path.exists(args.bbva):
        with open(args.bbva, "r", encoding="utf-8") as f:
            try:
                bbva_list = json.load(f)
            except json.JSONDecodeError:
                print(f"Error: {args.bbva} is not a valid JSON. Treating as empty.")
    else:
        print(f"Warning: {args.bbva} not found. Treating as empty.")

    santander_list = []
    if os.path.exists(args.santander):
        with open(args.santander, "r", encoding="utf-8") as f:
            try:
                santander_list = json.load(f)
            except json.JSONDecodeError:
                print(f"Error: {args.santander} is not a valid JSON. Treating as empty.")
    else:
        print(f"Warning: {args.santander} not found. Treating as empty.")

    unified_list = merge(bbva_list, santander_list)
    print(f"Merged {len(bbva_list)} BBVA and {len(santander_list)} Santander items into {len(unified_list)} unified items.")

    output_data = {
        "scraped_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "discounts": unified_list
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"Saved unified data to {args.output}")

if __name__ == "__main__":
    main()
