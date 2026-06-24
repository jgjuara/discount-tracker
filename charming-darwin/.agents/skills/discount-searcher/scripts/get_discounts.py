import subprocess
import json
import re
import argparse
import sys
import time
import os
import shutil
import urllib.request
import urllib.parse
import unicodedata

PROVINCES = [
    "CABA", "Buenos Aires", "Catamarca", "Chaco", "Chubut", "Córdoba", "Corrientes",
    "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza", "Misiones",
    "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe",
    "Santiago del Estero", "Tierra del Fuego", "Tucumán"
]

VALID_CATEGORIES = {
    "AUT", "DEP", "DIN", "EDU", "ESP", "FAR", "GAS", "HOG", "IND", "JUG", "LIB", "PELU", "PER", "SUP", "VAR", "VIA"
}
VALID_EXCLUSIVE = {
    "CPE", "MOD", "SEC", "SMI", "SOR"
}

def normalize_location(loc_str):
    if not loc_str:
        return ""
    
    def clean(s):
        s_norm = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')
        return s_norm.lower().strip()
    
    clean_input = clean(loc_str)
    for p in PROVINCES:
        if clean(p) == clean_input:
            return p
            
    raise ValueError(f"Ubicación no válida: '{loc_str}'. Ubicaciones válidas: {', '.join(PROVINCES)}")

def validate_category(cat):
    if not cat:
        return ""
    cat_upper = cat.upper().strip()
    if cat_upper in VALID_CATEGORIES or cat_upper in VALID_EXCLUSIVE:
        return cat_upper
    raise ValueError(f"Categoría no válida: '{cat}'. Categorías válidas: {', '.join(sorted(VALID_CATEGORIES | VALID_EXCLUSIVE))}")

def validate_days(days_str):
    if not days_str:
        return ""
    valid_days = {"-1", "0", "1", "2", "3", "4", "5", "6", "7"}
    parts = [p.strip() for p in days_str.split(",")]
    for part in parts:
        if part not in valid_days:
            raise ValueError(f"Día no válido: '{part}'. Días válidos: -1 (todos), 0-6 (Dom-Sab), 7 (hoy)")
    return ",".join(parts)

def validate_pay_with(pay_str):
    if not pay_str:
        return ""
    valid_payments = {"40", "41", "42", "43", "81", "M", "m"}
    pay_upper = pay_str.upper().strip()
    if pay_upper not in valid_payments:
        raise ValueError(f"Medio de pago no válido: '{pay_str}'. Medios de pago válidos: 40 (Visa Crédito), 41 (Mastercard), 42 (Amex), 43 (Visa Recargable), 81 (Visa Débito), M (MODO QR)")
    return pay_upper

def load_config(config_path, verbose=False):
    default_mens_footwear_brands = [
        "adidas", "nike", "puma", "reebok", "topper", "grimoldi", "hush puppies", "crocs", 
        "dexter", "moov", "sportline", "vans", "timberland", "caterpillar", "salomon", 
        "clarks", "fila", "converse", "new balance", "under armour", "asics", "dc shoes", 
        "bata", "briganti", "teran", "aldo", "superga", "montagne", "columbia", "merrell",
        "grid", "stock center", "open sports", "digitalsport", "chelsea", "dabra", "active sport",
        "calzados recorre", "calzados del valle", "calzados greits", "gianni deportes", 
        "luisa deportes", "sporting", "sportsman", "stadium sport", "sport tech store", 
        "ban sport", "gerónimo deportes", "go run", "just for sport", "mark sports",
        "angeloni deportes", "chiroqueta shoes"
    ]
    default_exclude_brands = [
        "cheeky", "mimo & co", "lazaro", "prune", "sarkany", "sofia sarkany", "baby junior", 
        "baruja toys", "bárbara bags", "osito azul jugueterías"
    ]
    
    if not config_path:
        # Check in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "discount_searcher_config.json")
        if not os.path.exists(config_path):
            if verbose:
                print(f"No config file path provided and default not found at '{config_path}'. Using built-in defaults.")
            return set(default_mens_footwear_brands), set(default_exclude_brands)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            mens_footwear = data.get("mens_footwear_brands", default_mens_footwear_brands)
            exclude = data.get("exclude_brands", default_exclude_brands)
            if verbose:
                print(f"Loaded brand configuration from: {config_path}")
            return set(mens_footwear), set(exclude)
    except Exception as e:
        if verbose:
            print(f"Warning: Failed to load config from '{config_path}': {e}. Using built-in defaults.")
        return set(default_mens_footwear_brands), set(default_exclude_brands)

def parse_args():
    parser = argparse.ArgumentParser(description="Query and process Santander discounts.")
    parser.add_argument("--category", type=str, default="", help="Category code (e.g., IND, SUP, GAS)")
    parser.add_argument("--exclusive", type=str, default="", help="Exclusive category code (e.g., SOR, SEC, MOD)")
    parser.add_argument("--days", type=str, default="", help="Days of week separated by commas (0-6, 7=today, -1=all)")
    parser.add_argument("--pay-with", type=str, default="", dest="pay_with", help="Payment method code (40, 41, 42, 81, M)")
    parser.add_argument("--location", type=str, default="", help="Province name (e.g., CABA, Buenos Aires, Córdoba)")
    parser.add_argument("--search", type=str, default="", help="Search text query")
    parser.add_argument("--output-json", type=str, default="", dest="output_json", help="Path to save JSON output")
    parser.add_argument("--output-md", type=str, default="", dest="output_md", help="Path to save Markdown report")
    parser.add_argument("--tag-mens-footwear", action="store_true", dest="tag_mens_footwear", help="Enable men's footwear tagging")
    parser.add_argument("--limit", type=int, default=50, help="Number of items to fetch per page (default: 50)")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries for API requests (default: 3)")
    parser.add_argument("--config", type=str, default="", help="Path to JSON configuration file for brand matching")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print debug information")
    return parser.parse_args()

def fetch_page(category, exclusive, days, pay_with, location, search, page, limit, verbose=False, retries=3):
    params = []
    if category:
        # Transparently map exclusive categories passed to --category
        if category in VALID_EXCLUSIVE:
            params.append(f"exclusive={category}")
        else:
            params.append(f"categories={category}")
    if exclusive:
        params.append(f"exclusive={exclusive}")
    if days:
        params.append(f"days={days}")
    if pay_with:
        params.append(f"pay_with={pay_with}")
    if location:
        params.append(f"location={urllib.parse.quote(location)}")
    if search:
        params.append(f"search={urllib.parse.quote(search)}")
        
    params.append(f"page={page}")
    params.append(f"limit={limit}")
    
    query_str = "&".join(params)
    url = f"https://www.santander.com.ar/bff-benefits/brands?{query_str}"
    
    use_curl = shutil.which("curl") or shutil.which("curl.exe")
    
    for attempt in range(1, retries + 1):
        if verbose:
            print(f"Fetching URL (Attempt {attempt}/{retries}): {url}")
            
        try:
            if use_curl:
                if verbose:
                    print("Using curl.exe for HTTP request...")
                cmd = ["curl.exe", "-s", url]
                result = subprocess.run(cmd, capture_output=True, timeout=15.0)
                if result.returncode != 0:
                    raise Exception(f"curl.exe exited with code {result.returncode}. Stderr: {result.stderr.decode('utf-8', errors='ignore')}")
                data_str = result.stdout.decode('utf-8', errors='ignore')
            else:
                if verbose:
                    print("curl.exe not found. Falling back to native urllib...")
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Referer": "https://www.santander.com.ar/personas/beneficios"
                })
                with urllib.request.urlopen(req, timeout=15.0) as response:
                    data_str = response.read().decode('utf-8', errors='ignore')
            
            return json.loads(data_str)
        except Exception as e:
            if verbose:
                print(f"Error on attempt {attempt}: {e}", file=sys.stderr)
            if attempt == retries:
                raise e
            # Exponential backoff
            time.sleep(attempt * 1.5)

def clean_discount_val(benefit_desc):
    if not benefit_desc:
        return 0
    
    # 1. Look for percentage first
    match = re.search(r'(\d+)\s*%', benefit_desc)
    if match:
        return int(match.group(1))
    
    # 2. Check for promo like 2x1, 3x2
    match_promo = re.search(r'(\d+)x(\d+)', benefit_desc.lower())
    if match_promo:
        val1 = int(match_promo.group(1))
        val2 = int(match_promo.group(2))
        if val1 > 0:
            return int(((val1 - val2) / val1) * 100)
    
    # 3. Check for financing phrases without percentage
    if "cuota" in benefit_desc.lower() or "financiación" in benefit_desc.lower():
        return 0
        
    # 4. Fallback to any standalone number
    match_num = re.search(r'(\d+)', benefit_desc)
    if match_num:
        return int(match_num.group(1))
        
    return 0

def get_group_sort_key(group_name):
    match = re.search(r'(\d+)', group_name)
    if match:
        return (0, -int(match.group(1))) # Percentage discounts sorted high to low
    elif "Financiación" in group_name or "Cuotas" in group_name:
        return (1, 0) # Financing next
    else:
        return (2, 0) # Others last

def main():
    args = parse_args()
    
    # Validation and Normalization
    try:
        category = validate_category(args.category)
        exclusive = validate_category(args.exclusive)
        days = validate_days(args.days)
        pay_with = validate_pay_with(args.pay_with)
        location = normalize_location(args.location)
    except ValueError as err:
        print(f"Validation Error: {err}", file=sys.stderr)
        sys.exit(1)
        
    limit = args.limit
    page = 1
    all_items = []
    total_items = None
    
    if args.verbose:
        print("Arguments validated successfully.")
        print(f"Normalized Category: {category or 'ALL'}, Exclusive: {exclusive or 'ALL'}, Days: {days or 'ALL'}, Pay-with: {pay_with or 'ALL'}, Location: {location or 'ALL'}")
        
    # Load brands configuration
    mens_footwear_brands, exclude_brands = load_config(args.config, args.verbose)
    
    print(f"Starting query for Category={category or 'ALL'}, Exclusive={exclusive or 'ALL'}, Days={days or 'ALL'}, Location={location or 'ALL'}...")
    
    while True:
        try:
            data = fetch_page(category, exclusive, days, pay_with, location, args.search, page, limit, args.verbose, args.retries)
            items = data.get("items", [])
            all_items.extend(items)
            
            if total_items is None:
                total_items = data.get("totalItems", 0)
                print(f"Total items matched on server: {total_items}")
                
            print(f"Fetched page {page} ({len(items)} items). Total collected: {len(all_items)}")
            
            if len(items) < limit or len(all_items) >= total_items or total_items == 0:
                break
                
            page += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"Error fetching page {page}: {e}", file=sys.stderr)
            break
            
    print(f"Fetched {len(all_items)} total brands.")
    
    processed = []
    for item in all_items:
        name = item.get("name", "").strip()
        benefit_desc = item.get("benefitDescription") or ""
        discount = clean_discount_val(benefit_desc)
        
        is_footwear = False
        if args.tag_mens_footwear:
            name_lower = name.lower()
            for fb in mens_footwear_brands:
                if fb in name_lower:
                    is_footwear = True
                    break
            for eb in exclude_brands:
                if eb in name_lower:
                    is_footwear = False
                    break
                    
        processed.append({
            "id": item.get("id"),
            "name": name,
            "benefit_desc": benefit_desc if benefit_desc else "N/A",
            "discount_val": discount,
            "is_mens_footwear": is_footwear
        })
        
    # Sort
    processed.sort(key=lambda x: (-x["discount_val"], x["name"].lower()))
    
    # Save JSON if requested
    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(processed, f, ensure_ascii=False, indent=2)
        print(f"JSON output saved to: {args.output_json}")
        
    # Save Markdown if requested
    if args.output_md:
        with open(args.output_md, "w", encoding="utf-8") as f:
            f.write(f"# Reporte de Descuentos de Santander\n\n")
            f.write(f"**Parámetros de consulta:**\n")
            f.write(f"- Categoría: `{category or 'Cualquiera'}`\n")
            if exclusive:
                f.write(f"- Exclusivo: `{exclusive}`\n")
            f.write(f"- Días: `{days or 'Cualquiera'}`\n")
            f.write(f"- Medio de Pago: `{pay_with or 'Cualquiera'}`\n")
            f.write(f"- Ubicación: `{location or 'Cualquiera'}`\n")
            f.write(f"- Búsqueda: `{args.search or 'Ninguna'}`\n\n")
            f.write(f"Total de comercios encontrados: {len(processed)}\n\n")
            
            # Group by discount_val
            groups = {}
            for b in processed:
                val = b["discount_val"]
                desc = b["benefit_desc"]
                if ("cuota" in desc.lower() or "financiación" in desc.lower()) and val == 0:
                    g_key = "Solo Financiación (Cuotas sin Interés)"
                elif val == 0:
                    g_key = "Otros Beneficios"
                else:
                    g_key = f"{val}% de Descuento"
                    
                if g_key not in groups:
                    groups[g_key] = []
                groups[g_key].append(b)
                
            # Sort keys safely
            sorted_keys = sorted(groups.keys(), key=get_group_sort_key)
            
            for g_key in sorted_keys:
                f.write(f"## {g_key}\n")
                f.write(f"Total: {len(groups[g_key])} comercios\n\n")
                f.write("| Comercio | Beneficio | Calzado Hombre |\n")
                f.write("| :--- | :---: | :---: |\n")
                for b in groups[g_key]:
                    footwear_tag = "👟 Sí" if b["is_mens_footwear"] else "No"
                    f.write(f"| {b['name']} | {b['benefit_desc']} | {footwear_tag} |\n")
                f.write("\n")
                
        print(f"Markdown report saved to: {args.output_md}")

if __name__ == "__main__":
    main()
