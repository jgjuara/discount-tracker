import json
import re

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
    r'\btommy\s+hilfiger\b'
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
    r'\bpuma\b'
]

GENERAL_BRANDS = {
    'zara', 'nike', 'vans', 'adidas', 'puma', 'topper', 'dexter', 'moov', 'grid', 'stock center'
}

ROPA_KEYWORDS = ["hombre", "masculino", "camisa", "pantalon", "remera", "campera", "jean"]
CALZADO_KEYWORDS = ["calzado", "zapatilla", "zapato", "bota", "nautico", "náutico"]

def classify_promotion(cabecera, subcabecera):
    c_lower = cabecera.lower()
    s_lower = subcabecera.lower()
    full_text = f"{c_lower} {s_lower}"

    has_ropa_brand = any(re.search(p, full_text) for p in ROPA_BRANDS)
    has_calzado_brand = any(re.search(p, full_text) for p in CALZADO_BRANDS)
    
    has_general_brand = False
    for gb in GENERAL_BRANDS:
        if re.search(r'\b' + re.escape(gb) + r'\b', full_text):
            has_general_brand = True
            break

    ropa_keyword_detected = any(kw in full_text for kw in ROPA_KEYWORDS)
    calzado_keyword_detected = any(kw in full_text for kw in CALZADO_KEYWORDS)

    if has_general_brand:
        if ropa_keyword_detected and not calzado_keyword_detected:
            return "ropa"
        elif calzado_keyword_detected and not ropa_keyword_detected:
            return "calzado"
        else:
            return "both"
    else:
        if has_ropa_brand or has_calzado_brand or ropa_keyword_detected or calzado_keyword_detected:
            return "classified"
    return None

def main():
    import requests
    all_promos = []
    pager = 0
    while True:
        params = {"pager": pager, "rubros": 170}
        res = requests.get("https://go.bbva.com.ar/willgo/fgo/API/v3/communications", headers={
            "accept": "*/*",
            "accept-language": "es-AR,es-US;q=0.9,es;q=0.8",
            "origin": "https://www.bbva.com.ar",
            "referer": "https://www.bbva.com.ar/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
        }, params=params, timeout=15)
        if res.status_code != 200:
            break
        data = res.json().get("data", [])
        if not data:
            break
        all_promos.extend(data)
        pager += 1
        
    with open("scratch/unclassified_list.txt", "w", encoding="utf-8") as f:
        for p in all_promos:
            cabecera = p.get("cabecera", "")
            subcabecera = p.get("subcabecera", "")
            c_type = classify_promotion(cabecera, subcabecera)
            if c_type is None:
                f.write(f"ID: {p.get('id')} | Cabecera: {cabecera} | Subcabecera: {subcabecera}\n")

if __name__ == "__main__":
    main()
