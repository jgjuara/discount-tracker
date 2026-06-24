import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://go.bbva.com.ar/willgo/fgo/API/v3"

HEADERS = {
    "accept": "*/*",
    "accept-language": "es-AR,es-US;q=0.9,es;q=0.8,en-US;q=0.7,en;q=0.6,es-419;q=0.5",
    "origin": "https://www.bbva.com.ar",
    "referer": "https://www.bbva.com.ar/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
}

def make_request(url, params=None, method="GET"):
    try:
        response = requests.request(method, url, headers=HEADERS, params=params, timeout=10)
        res_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content_type": response.headers.get("content-type", ""),
        }
        try:
            res_data["json"] = response.json()
        except Exception:
            res_data["text"] = response.text[:2000] # Cap text representation to avoid huge outputs
        return res_data
    except Exception as e:
        return {"error": str(e)}

def probe_endpoints():
    print("Probing endpoints...")
    endpoints = {
        "rubros": f"{BASE_URL}/rubros",
        "categories": f"{BASE_URL}/categories",
        "filters": f"{BASE_URL}/filters",
        "config": f"{BASE_URL}/config",
        "subrubros": f"{BASE_URL}/subrubros",
        "communications_detail_85443": f"{BASE_URL}/communications/85443",
        "communication_detail_85443": f"{BASE_URL}/communication/85443",
    }
    
    results = {}
    for name, url in endpoints.items():
        print(f"  Testing {name}: {url}")
        results[name] = {
            "url": url,
            "response": make_request(url)
        }
        time.sleep(0.5)
    return results

def probe_rubro(rubro_id):
    url = f"{BASE_URL}/communications"
    params = {"pager": 0, "rubros": rubro_id}
    res = make_request(url, params=params)
    time.sleep(0.1)  # Small delay between concurrent tasks
    return rubro_id, res

def scan_rubros():
    print("Scanning rubros 1 to 300...")
    active_rubros = {}
    errors = {}
    empty_rubros = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(probe_rubro, i): i for i in range(1, 301)}
        for future in as_completed(futures):
            rubro_id = futures[future]
            try:
                rubro_id, res = future.result()
                if "error" in res:
                    errors[rubro_id] = res["error"]
                elif res.get("status_code") != 200:
                    errors[rubro_id] = f"Status {res.get('status_code')}"
                else:
                    json_data = res.get("json", {})
                    data_list = json_data.get("data", [])
                    msg = json_data.get("message", "")
                    code = json_data.get("code", -1)
                    
                    if code == 0 and len(data_list) > 0:
                        # Extract some info about this rubro
                        first_promo = data_list[0]
                        active_rubros[rubro_id] = {
                            "count": len(data_list),
                            "message": msg,
                            "sample_cabecera": first_promo.get("cabecera"),
                            "sample_subcabecera": first_promo.get("subcabecera"),
                            "sample_card": first_promo.get("grupoTarjeta"),
                            "sample_id": first_promo.get("id"),
                        }
                        print(f"  Rubro {rubro_id}: ACTIVE ({len(data_list)} promos) - e.g., {first_promo.get('cabecera')}")
                    else:
                        empty_rubros.append(rubro_id)
            except Exception as e:
                errors[rubro_id] = str(e)
                
    return {
        "active": active_rubros,
        "empty_count": len(empty_rubros),
        "empty_list": sorted(empty_rubros),
        "errors": errors
    }

def test_pagination():
    print("Testing pagination...")
    pages = [0, 1, 16, 17, 18, -1, "abc"]
    results = {}
    url = f"{BASE_URL}/communications"
    
    for p in pages:
        params = {"pager": p, "rubros": 170}
        print(f"  Testing pager={p}...")
        results[str(p)] = {
            "params": params,
            "response": make_request(url, params=params)
        }
        time.sleep(0.5)
    return results

def test_query_parameters():
    print("Testing other potential parameters...")
    # Based on the results of communications, we know Zara exists.
    # Let's test with rubros=170 and overall search parameters.
    test_cases = [
        {"q": "zara"},
        {"query": "zara"},
        {"search": "zara"},
        {"texto": "zara"},
        {"provincia": "buenos aires"},
        {"provincia": "1"},
        {"orden": "asc"},
        {"sort": "desc"},
        {"rubros": 170, "q": "zara"},
        {"rubros": 170, "texto": "zara"},
    ]
    
    results = {}
    url = f"{BASE_URL}/communications"
    
    for tc in test_cases:
        params = {"pager": 0, **tc}
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        print(f"  Testing parameters: {param_str}...")
        results[param_str] = {
            "params": params,
            "response": make_request(url, params=params)
        }
        time.sleep(0.5)
    return results

def main():
    start_time = time.time()
    
    endpoint_results = probe_endpoints()
    rubro_results = scan_rubros()
    pagination_results = test_pagination()
    param_results = test_query_parameters()
    
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": time.time() - start_time,
        "endpoints": endpoint_results,
        "rubros_scan": rubro_results,
        "pagination": pagination_results,
        "parameters": param_results
    }
    
    with open("scratch/probe_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        
    print(f"\nDone! Results saved in scratch/probe_results.json. Execution took {output['elapsed_seconds']:.2f} seconds.")

if __name__ == "__main__":
    main()
