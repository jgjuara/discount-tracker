import json
import re
import time
import requests

BASE_URL = "https://go.bbva.com.ar/willgo/fgo/API/v3/communications"
RUBROS_ID = 170

HEADERS = {
    "accept": "*/*",
    "accept-language": "es-AR,es-US;q=0.9,es;q=0.8",
    "origin": "https://www.bbva.com.ar",
    "referer": "https://www.bbva.com.ar/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
}

ROPA_BRANDS = [
    r'\brever\s+pass\b',
    r'\bherencia\b',
    r'\bzara\b',
    r'\blevi\'?s\b',
    r'\bmacowens\b',
    r'\bequus\b',
    r'\bpenguin\b',
    r'\brochas\b',
    r'\bbowen\b',
    r'\blacoste\b',
    r'\btommy\b',
    r'\btommy\s+hilfiger\b',
    r'\bdevre\b',
    r'\bkevingston\b',
    r'\bvincenzo\b',
    r'\bmistral\b',
    r'\bgenoa\b',
    r'\bubatuba\b',
    r'\bcollege\b',
    r'\bamerican\s+truck\b'
]

CALZADO_BRANDS = [
    r'\bnike\b',
    r'\bvans\b',
    r'\bcat\b',
    r'\bhush\s+puppies\b',
    r'\bchelsea\b',
    r'\btop\s+sport\b',
    r'\bsarkany\b',
    r'\bdexter\b',
    r'\bmoov\b',
    r'\bgrid\b',
    r'\bstock\s+center\b',
    r'\btopper\b',
    r'\badidas\b',
    r'\bpuma\b',
    r'\bgrimoldi\b',
    r'\bmerrell\b',
    r'\bposco\b',
    r'\bjm\s+shoes\b'
]

# General Brands that offer both clothing and footwear
GENERAL_BRANDS = {
    'zara', 'nike', 'vans', 'adidas', 'puma', 'topper', 'dexter', 'moov', 'grid', 'stock center',
    'the north face', 'pampero', 'decathlon', 'under armour', 'champion', 'mizuno', 'bullpadel'
}

# Regex to detect sports retailers which sell both clothing and footwear (e.g. Seven Sport, Sport 78)
# We exclude "transport" using a negative lookahead to avoid false positives on transport/envío info.
SPORT_RETAILER_PATTERN = re.compile(r'\b(?!transport)\w*(?:deport|sport|hockey)\w*\b', re.IGNORECASE)

ROPA_KEYWORDS = ["hombre", "masculino", "camisa", "pantalon", "remera", "campera", "jean"]
CALZADO_KEYWORDS = ["calzado", "zapatilla", "zapato", "bota", "nautico", "náutico"]

def extract_discount_and_cuotas(cabecera, subcabecera):
    # Try to extract discount percentage
    discount = 0
    pct_match = re.search(r'(\d+)\s*%', cabecera)
    if not pct_match:
        pct_match = re.search(r'(\d+)\s*%', subcabecera)
    if pct_match:
        discount = int(pct_match.group(1))

    # Try to extract cuotas
    cuotas = 0
    cuota_matches = re.findall(r'(\d+)\s*cuotas?', cabecera, re.IGNORECASE) + \
                    re.findall(r'(\d+)\s*cuotas?', subcabecera, re.IGNORECASE)
    if cuota_matches:
        cuotas = max(int(m) for m in cuota_matches)

    return discount, cuotas

def classify_promotion(cabecera, subcabecera):
    c_lower = cabecera.lower()
    s_lower = subcabecera.lower()
    full_text = f"{c_lower} {s_lower}"

    is_ropa = False
    is_calzado = False

    # Check for brands
    has_ropa_brand = any(re.search(p, full_text) for p in ROPA_BRANDS)
    has_calzado_brand = any(re.search(p, full_text) for p in CALZADO_BRANDS)
    
    # Check if general brand
    is_general = False
    for gb in GENERAL_BRANDS:
        if re.search(r'\b' + re.escape(gb) + r'\b', full_text):
            is_general = True
            break
            
    # Check sport retailer pattern
    if not is_general and SPORT_RETAILER_PATTERN.search(full_text):
        is_general = True

    # Check keywords
    has_ropa_keyword = any(kw in full_text for kw in ROPA_KEYWORDS)
    has_calzado_keyword = any(kw in full_text for kw in CALZADO_KEYWORDS)

    if is_general:
        # Zara, Nike, Seven Sport, etc. - put in both unless keywords restrict
        if has_ropa_keyword and not has_calzado_keyword:
            is_ropa = True
        elif has_calzado_keyword and not has_ropa_keyword:
            is_calzado = True
        else:
            # store-wide or both keywords
            is_ropa = True
            is_calzado = True
    else:
        # Non-general brand or keyword-based
        if has_ropa_brand:
            is_ropa = True
        if has_calzado_brand:
            is_calzado = True

        # Check keywords if no specific brands matched
        if not has_ropa_brand and not has_calzado_brand:
            if has_ropa_keyword:
                is_ropa = True
            if has_calzado_keyword:
                is_calzado = True

    return is_ropa, is_calzado

def fetch_all_promotions():
    all_promos = []
    pager = 0
    print("Starting API download for rubros=170...")
    while True:
        params = {"pager": pager, "rubros": RUBROS_ID}
        print(f"Fetching page {pager}...")
        try:
            res = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
            if res.status_code != 200:
                print(f"Error fetching page {pager}: status {res.status_code}")
                break
            
            data_json = res.json()
            promos = data_json.get("data", [])
            if not promos:
                print(f"No data returned on page {pager}. Stopping download.")
                break
            
            all_promos.extend(promos)
            print(f"Successfully retrieved {len(promos)} promotions from page {pager}.")
            pager += 1
            time.sleep(0.3)  # Polite delay
        except Exception as e:
            print(f"Exception during request: {e}")
            break
            
    print(f"Total raw promotions downloaded: {len(all_promos)}")
    return all_promos

def main():
    raw_promos = fetch_all_promotions()
    if not raw_promos:
        print("No promotions downloaded. Exiting.")
        return
        
    ropa_list = []
    calzado_list = []
    unclassified_count = 0
    
    # Process, parse, and classify
    for p in raw_promos:
        cabecera = p.get("cabecera", "")
        subcabecera = p.get("subcabecera", "")
        
        discount, cuotas = extract_discount_and_cuotas(cabecera, subcabecera)
        is_ropa, is_calzado = classify_promotion(cabecera, subcabecera)
        
        processed_item = {
            "id": p.get("id"),
            "cabecera": cabecera,
            "subcabecera": subcabecera,
            "imagen": p.get("imagen"),
            "fechaDesde": p.get("fechaDesde"),
            "fechaHasta": p.get("fechaHasta"),
            "grupoTarjeta": p.get("grupoTarjeta"),
            "discount_percentage": discount,
            "cuotas": cuotas
        }
        
        classified = False
        if is_ropa:
            ropa_list.append(processed_item)
            classified = True
        if is_calzado:
            calzado_list.append(processed_item)
            classified = True
            
        if not classified:
            unclassified_count += 1
            
    # Sort from highest to lowest discount (discount first, then cuotas)
    ropa_sorted = sorted(ropa_list, key=lambda x: (x["discount_percentage"], x["cuotas"]), reverse=True)
    calzado_sorted = sorted(calzado_list, key=lambda x: (x["discount_percentage"], x["cuotas"]), reverse=True)
    
    # Output structure
    output_data = {
        "ropa_de_hombres": ropa_sorted,
        "calzado_de_hombres": calzado_sorted
    }
    
    # Save JSON file
    output_file = "scratch/men_discounts.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"Saved classified results to {output_file}")
    print(f"Stats:")
    print(f"  - Ropa de hombres: {len(ropa_sorted)}")
    print(f"  - Calzado de hombres: {len(calzado_sorted)}")
    print(f"  - Unclassified (ignored): {unclassified_count}")
    
    # Generate Markdown Report
    report_file = "scratch/men_discounts_report.md"
    
    total_ropa = len(ropa_sorted)
    total_calzado = len(calzado_sorted)
    
    # Find top discount in each
    top_ropa = ropa_sorted[0] if ropa_sorted else None
    top_calzado = calzado_sorted[0] if calzado_sorted else None
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Reporte de Promociones de Moda y Accesorios (BBVA Go - Rubro 170)\n\n")
        f.write("Este reporte consolida y clasifica las promociones del rubro 170 de la API de BBVA Go filtradas para hombres en las categorías de **Ropa de hombres** y **Calzado de hombres**, ordenadas de mayor a menor descuento.\n\n")
        
        f.write("## Supuestos y Consideraciones\n")
        f.write("- Se descargaron las promociones desde `pager=0` hasta agotar las páginas de resultados de la API de BBVA Go (hasta `pager=16`).\n")
        f.write("- Para determinar el porcentaje de descuento y las cuotas sin interés se analizaron los campos `cabecera` y `subcabecera` usando expresiones regulares.\n")
        f.write("- Las marcas generales (como Zara, Nike, Vans, Topper, Dexter, Moov, Grid, Stock Center, Adidas, Puma, The North Face, Pampero, Decathlon, etc.) y las tiendas de deportes (identificadas por patrones como 'sport' o 'deport') que comercializan tanto indumentaria como calzado fueron clasificadas en ambas categorías, a menos que las palabras clave de la promoción restringieran su aplicación a una sola categoría.\n")
        f.write("- Las promociones se ordenaron de mayor a menor descuento, priorizando el porcentaje de reintegro y secundariamente el número de cuotas sin interés.\n\n")
        
        f.write("## Resumen Estadístico\n")
        f.write(f"- **Total de promociones analizadas (Rubro 170):** {len(raw_promos)}\n")
        f.write(f"- **Clasificadas como Ropa de Hombres:** {total_ropa}\n")
        f.write(f"- **Clasificadas como Calzado de Hombres:** {total_calzado}\n")
        f.write(f"- **Promociones omitidas (ópticas, joyerías, locales de mujer/niños):** {unclassified_count}\n\n")
        
        f.write("## Destacados (Mejores Descuentos)\n")
        if top_ropa:
            f.write(f"### Mejor Promoción en Ropa de Hombres\n")
            f.write(f"- **Comercio:** {top_ropa['cabecera']}\n")
            f.write(f"- **Detalle:** {top_ropa['subcabecera']}\n")
            f.write(f"- **Descuento:** {top_ropa['discount_percentage']}% | **Cuotas:** {top_ropa['cuotas']}\n\n")
            
        if top_calzado:
            f.write(f"### Mejor Promoción en Calzado de Hombres\n")
            f.write(f"- **Comercio:** {top_calzado['cabecera']}\n")
            f.write(f"- **Detalle:** {top_calzado['subcabecera']}\n")
            f.write(f"- **Descuento:** {top_calzado['discount_percentage']}% | **Cuotas:** {top_calzado['cuotas']}\n\n")
            
        f.write("## Detalle de Promociones por Categoría (Top 15)\n\n")
        
        f.write("### Ropa de Hombres (Top 15)\n")
        f.write("| Comercio / Cabecera | Detalle / Subcabecera | Reintegro (%) | Cuotas |\n")
        f.write("| --- | --- | :---: | :---: |\n")
        for item in ropa_sorted[:15]:
            f.write(f"| {item['cabecera']} | {item['subcabecera']} | {item['discount_percentage']}% | {item['cuotas']} |\n")
        f.write("\n")
        
        f.write("### Calzado de Hombres (Top 15)\n")
        f.write("| Comercio / Cabecera | Detalle / Subcabecera | Reintegro (%) | Cuotas |\n")
        f.write("| --- | --- | :---: | :---: |\n")
        for item in calzado_sorted[:15]:
            f.write(f"| {item['cabecera']} | {item['subcabecera']} | {item['discount_percentage']}% | {item['cuotas']} |\n")
            
    print(f"Report written to {report_file}")

if __name__ == "__main__":
    main()
