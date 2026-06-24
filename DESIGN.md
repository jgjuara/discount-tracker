# Documento de Diseño — Discount Tracker Argentina

> **Estado:** Borrador v1.0 | **Fecha:** 2026-06-23

---

## 1. Resumen del Proyecto

### Propósito

Construir una aplicación web estática, pública y de acceso libre que consolide y unifique las promociones y descuentos vigentes publicados por **BBVA Argentina** (via BBVA Go) y **Santander Argentina** en una única interfaz de búsqueda. El objetivo es eliminar la fricción de consultar múltiples portales bancarios con taxonomías inconsistentes.

### Usuarios Objetivo

- Consumidores argentinos con tarjetas de crédito/débito de BBVA o Santander que desean maximizar sus descuentos antes de realizar una compra.
- Usuarios que navegan sin sesión activa en ninguno de los dos bancos y que no desean autenticarse en portales bancarios para ver promociones públicas.

### No-Goals

- No se implementará autenticación de usuarios.
- No se almacenarán datos personales ni se integrará ningún sistema bancario que requiera credenciales del usuario.
- No se realizarán llamadas a las APIs bancarias desde el navegador del cliente.
- No se cubrirán bancos adicionales en la v1 (Galicia, Naranja X, etc.).
- No se ofrecerá geolocalización de sucursales (los datos de coordenadas de BBVA se descartan en v1).

---

## 2. Estructura del Repositorio

```
discount-tracker/
├── .github/
│   └── workflows/
│       ├── scrape.yml          # Cron diario: extrae y cachea datos
│       └── deploy.yml          # Despliega la web app en GitHub Pages
├── scrapers/
│   ├── __init__.py
│   ├── taxonomy.py             # Taxonomía canónica unificada
│   ├── merger.py               # Fusiona y normaliza salidas de ambos scrapers
│   ├── requirements.txt        # requests, tenacity
│   ├── bbva/
│   │   ├── __init__.py
│   │   ├── scraper.py          # Scraper principal BBVA
│   │   └── normalizer.py       # Transforma respuesta BBVA al schema unificado
│   └── santander/
│       ├── __init__.py
│       ├── scraper.py          # Scraper principal Santander
│       └── normalizer.py       # Transforma respuesta Santander al schema unificado
├── data/
│   ├── bbva.json               # Descuentos BBVA normalizados (generado por CI)
│   ├── santander.json          # Descuentos Santander normalizados (generado por CI)
│   └── unified.json            # Dataset unificado de ambos bancos (generado por CI)
├── web/                        # SvelteKit app
│   ├── src/
│   │   ├── app.html
│   │   ├── app.css             # Design tokens y estilos globales
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   │   ├── SearchBar.svelte
│   │   │   │   ├── FilterPanel.svelte
│   │   │   │   ├── DiscountCard.svelte
│   │   │   │   ├── DiscountGrid.svelte
│   │   │   │   └── BankBadge.svelte
│   │   │   ├── stores/
│   │   │   │   └── discounts.js
│   │   │   └── utils/
│   │   │       └── search.js
│   │   └── routes/
│   │       ├── +page.svelte
│   │       ├── +page.js
│   │       └── descuento/
│   │           └── [bank]/
│   │               └── [id]/
│   │                   ├── +page.svelte
│   │                   └── +page.js
│   ├── static/
│   │   └── favicon.svg
│   ├── svelte.config.js
│   ├── vite.config.js
│   └── package.json
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── requirements-test.txt
│   ├── test_bbva_scraper.py
│   ├── test_santander_scraper.py
│   ├── test_taxonomy.py
│   └── test_unified_merger.py
├── adventurous-euclid/         # Investigación y prototipado BBVA (legacy)
├── charming-darwin/            # Investigación y prototipado Santander (legacy)
├── DESIGN.md
└── README.md
```

---

## 3. Taxonomía Canónica Unificada

La taxonomía mapea categorías heterogéneas de ambos bancos a un conjunto canónico compartido. La clave canónica es la que el frontend usa para filtrar.

| `canonical_key`       | `display_name_es`              | `icon_emoji` | `bbva_rubros` (IDs) | `santander_categories` (STA) |
|-----------------------|--------------------------------|:------------:|---------------------|------------------------------|
| `gastronomia`         | Gastronomía y Restoranes       | 🍽️           | 3                   | GAS, DIN                     |
| `entretenimiento`     | Entretenimiento y Espectáculos | 🎭           | 4                   | ESP                          |
| `cuidado_personal`    | Cuidado Personal y Farmacias   | 💊           | 8                   | FAR, PELU, PER               |
| `turismo`             | Viajes y Turismo               | ✈️           | 13                  | VIA                          |
| `supermercados`       | Supermercados                  | 🛒           | 26                  | SUP                          |
| `moda`                | Moda e Indumentaria            | 👗           | 170                 | IND                          |
| `hogar`               | Hogar y Decoración             | 🏠           | 173                 | HOG                          |
| `automotores`         | Automotores y Servicios        | 🚗           | 174                 | AUT                          |
| `infantil`            | Jugueterías e Infantiles       | 🧸           | 175                 | JUG                          |
| `deportes`            | Deportes y Educación           | 🏋️           | 184                 | DEP, EDU                     |
| `tecnologia`          | Electro y Tecnología           | 📱           | 192                 | *(sin STA directo)*          |
| `bazar`               | Bazar, Regalos y Vinos         | 🎁           | 195                 | VAR                          |
| `libros`              | Librerías y Cultura            | 📚           | *(sin rubro BBVA)*  | LIB                          |

**Notas:**
- BBVA rubro 192 (Electro/Tecnología) no tiene STA equivalente en Santander; marcas de tecnología de Santander aparecen bajo `VAR` y se reclasifican en el merger.
- Santander `LIB` no tiene rubro BBVA equivalente; solo aparece desde Santander.
- Categorías EXC de Santander (`CPE`, `MOD`, `SEC`, `SMI`, `SOR`) se mapean como categorías propias del frontend bajo claves `cuidado_personal` (CPE) y claves especiales (`modo_digital`, `select`, `super_miercoles`, `sorpresa`).

---

## 4. Arquitectura de Scrapers

### 4.1 Estructura del Paquete Python

```
scrapers/
├── __init__.py
├── taxonomy.py      # BBVA_RUBRO_MAP, SANTANDER_CAT_MAP, CANONICAL_CATEGORIES
├── merger.py        # merge(bbva_list, santander_list) -> unified_list
├── bbva/
│   ├── __init__.py
│   ├── scraper.py   # BBVAScraper class
│   └── normalizer.py
└── santander/
    ├── __init__.py
    ├── scraper.py   # SantanderScraper class
    └── normalizer.py
```

### 4.2 Scraper BBVA

**Headers requeridos** (sin estos el servidor retorna HTTP 403 o 400):
```python
HEADERS = {
    "accept": "*/*",
    "accept-language": "es-AR,es-US;q=0.9,es;q=0.8",
    "origin": "https://www.bbva.com.ar",
    "referer": "https://www.bbva.com.ar/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ..."
}
```

**Rubros activos** (IDs validados mediante barrido 1-300):
```python
ACTIVE_RUBROS = [3, 4, 8, 13, 26, 170, 173, 174, 175, 184, 192, 195]
```

**Lógica de paginación:**
```
Para cada rubro_id en ACTIVE_RUBROS:
    pager = 0
    mientras True:
        GET /communications?pager={pager}&rubros={rubro_id}
        si response.status != 200: raise BBVAScraperError
        si response.json()["data"] == []: break   # fin de paginas
        acumular data
        pager += 1
        sleep(0.3)   # delay cortés entre requests
```

**Manejo de errores y reintentos:**
- HTTP 500 (pager inválido): capturar, loguear warning, skip del rubro.
- Timeout (10s): reintentar hasta 3 veces con backoff exponencial (1s → 2s → 4s).
- Cualquier otro status != 200: raise `BBVAScraperError`.

### 4.3 Scraper Santander

**URL base:** `https://www.santander.com.ar`

**Lógica de extracción completa:**
```
# Fase 1: Categorias estandar (STA)
STA_CATEGORIES = ["AUT","DEP","DIN","EDU","ESP","FAR","GAS","HOG","IND","JUG","LIB","PELU","PER","SUP","VAR","VIA"]
Para cada category_code en STA_CATEGORIES:
    page = 1
    mientras True:
        GET /bff-benefits/brands?categories={code}&page={page}&limit=50
        si brands == []: break
        Para cada brand en brands:
            GET /bff-benefits/brands/{brand.id}
            acumular publicaciones normalizadas
        page += 1
        sleep(0.5)

# Fase 2: Programas exclusivos (EXC)
EXC_CATEGORIES = ["CPE","MOD","SEC","SMI","SOR"]
Para cada exc_code en EXC_CATEGORIES:
    # mismo loop de paginacion con ?exclusive={exc_code}
```

**Nota:** El scraper omite el parámetro `location` para obtener cobertura nacional completa. Los filtros por provincia se aplican en el frontend (v2).

**Manejo de errores:**
- HTTP 429: esperar 60s y reintentar.
- HTTP 503: reintentar 3 veces con backoff exponencial.
- Timeout (15s): reintentar 3 veces.

### 4.4 Schema Unificado — Normalized Discount Object

```json
{
  "id": "bbva-85443",
  "bank": "bbva",
  "canonical_category": "moda",
  "store_name": "Zara",
  "title": "Zara 3 cuotas",
  "description": "Hasta 3 cuotas sin interés. Válida del 01/06/2026 al 30/06/2026.",
  "discount_pct": 0,
  "installments": 3,
  "valid_from": "2026-06-01",
  "valid_until": "2026-06-30",
  "days_active": [0, 1, 2, 3, 4, 5, 6],
  "card_types": ["credito_bbva"],
  "url": "https://zara.com/ar",
  "image_url": "https://go.bbva.com.ar/fgo/sites/default/files/...",
  "raw": {}
}
```

| Campo                | Tipo             | Descripción                                                          |
|----------------------|------------------|----------------------------------------------------------------------|
| `id`                 | `string`         | `{bank}-{original_id}`. Unicidad global garantizada.                 |
| `bank`               | `"bbva"\|"santander"` | Origen del descuento.                                          |
| `canonical_category` | `string`         | Clave canónica según taxonomía §3.                                   |
| `store_name`         | `string`         | Nombre del comercio.                                                 |
| `title`              | `string`         | Título corto de la promoción.                                        |
| `description`        | `string`         | Descripción extendida.                                               |
| `discount_pct`       | `integer`        | Porcentaje de descuento. 0 si la promo es solo cuotas.               |
| `installments`       | `integer`        | Máximo de cuotas sin interés. 0 si no aplica.                        |
| `valid_from`         | `string`         | ISO 8601 fecha inicio. `null` si no disponible.                      |
| `valid_until`        | `string`         | ISO 8601 fecha fin. `null` si no disponible.                         |
| `days_active`        | `array[int]`     | Días activos (0=Dom..6=Sáb). `[-1]` = todos los días.               |
| `card_types`         | `array[string]`  | Ej: `["credito_visa", "mastercard", "debito_visa"]`.                 |
| `url`                | `string\|null`   | URL de compra online.                                                |
| `image_url`          | `string\|null`   | URL de imagen del comercio.                                          |
| `raw`                | `object`         | Respuesta original sin modificar (para auditoría y debugging).       |

---

## 5. GitHub Actions Workflow

### 5.1 `scrape.yml` — Extracción y caché diaria

```yaml
name: Daily Scrape

on:
  schedule:
    - cron: '0 6 * * *'   # 06:00 UTC = 03:00 ART
  workflow_dispatch:        # Permite disparo manual

jobs:
  scrape:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r scrapers/requirements.txt

      - name: Run BBVA scraper
        run: python -m scrapers.bbva.scraper --output data/bbva.json

      - name: Run Santander scraper
        run: python -m scrapers.santander.scraper --output data/santander.json

      - name: Merge datasets
        run: python -m scrapers.merger --bbva data/bbva.json --santander data/santander.json --output data/unified.json

      - name: Commit and push data
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/
          git diff --staged --quiet || git commit -m "chore(data): daily scrape $(date -u +%Y-%m-%d)"
          git push

      - name: Trigger deploy
        uses: benc-uk/workflow-dispatch@v1
        with:
          workflow: deploy.yml
          token: ${{ secrets.GITHUB_TOKEN }}
```

### 5.2 `deploy.yml` — Despliegue en GitHub Pages

```yaml
name: Deploy to GitHub Pages

on:
  workflow_dispatch:
  push:
    paths: ['data/**', 'web/**']

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: web/package-lock.json

      - name: Copy data to web static
        run: cp -r data/ web/static/data/

      - name: Build SvelteKit
        working-directory: web
        run: |
          npm ci
          npm run build

      - uses: actions/upload-pages-artifact@v3
        with:
          path: web/build

      - uses: actions/deploy-pages@v4
```

### 5.3 Estrategia de Caché

- Los archivos `data/*.json` se almacenan **en el repositorio** como archivos versionados (no en caché de Actions).
- Si el scraper falla en un día, el JSON de la ejecución anterior permanece en repo (degradación controlada).
- El frontend importa `unified.json` en build time; cero llamadas de red en runtime.
- El campo `scraped_at` en `unified.json` permite al frontend mostrar un banner de alerta si los datos tienen más de 25 horas.

---

## 6. Diseño de la Web App (SvelteKit)

### 6.1 Rutas

| Ruta                      | Descripción                                    |
|---------------------------|------------------------------------------------|
| `/`                       | Home: barra de búsqueda + grilla de resultados |
| `/descuento/[bank]/[id]`  | Vista de detalle de un descuento específico    |

### 6.2 Carga de Datos

```javascript
// web/src/routes/+page.js
// Importación estática en build time — sin fetch en runtime
import unifiedData from '$lib/data/unified.json';

export function load() {
  return { discounts: unifiedData };
}
```

### 6.3 Componentes

| Componente       | Responsabilidad                                                               |
|------------------|-------------------------------------------------------------------------------|
| `SearchBar`      | Input de texto libre; dispara evento `search` con el término.                  |
| `FilterPanel`    | Controles para: categoría canónica, banco, día de semana, tipo de tarjeta.    |
| `DiscountCard`   | Tarjeta: imagen, título, tienda, % descuento, cuotas, `BankBadge`.           |
| `DiscountGrid`   | Grid CSS responsivo que renderiza la lista filtrada de `DiscountCard`.         |
| `BankBadge`      | Chip visual con color de banco (BBVA = `#004A97`, Santander = `#EC0000`).     |

### 6.4 Lógica de Búsqueda (`src/lib/utils/search.js`)

```javascript
export function filterDiscounts(discounts, { query, category, bank, day, card }) {
  return discounts.filter(d => {
    if (query) {
      const q = query.toLowerCase();
      const match = [d.store_name, d.title, d.description]
        .some(f => f?.toLowerCase().includes(q));
      if (!match) return false;
    }
    if (category && d.canonical_category !== category) return false;
    if (bank && d.bank !== bank) return false;
    if (day !== null && day !== undefined) {
      if (!d.days_active.includes(-1) && !d.days_active.includes(day)) return false;
    }
    if (card && !d.card_types.includes(card)) return false;
    return true;
  });
}
```

### 6.5 UI/UX

- **Paleta:** Fondo `#0f0f0f`, superficie `#1a1a1a`, acento BBVA `#004A97`, acento Santander `#EC0000`, texto `#f0f0f0`.
- **Tipografía:** `Inter` (Google Fonts), pesos 400/500/700.
- **Layout:** Grid 1 col (mobile) → 2 col (tablet) → 3-4 col (desktop).
- **Modo:** Solo dark mode en v1.
- **Animaciones:** `transition: opacity 150ms ease, transform 150ms ease` en hover de tarjetas.
- **CSS:** Vanilla CSS puro. Sin frameworks de UI.

---

## 7. Fases de Desarrollo y Hitos

| Fase | Entregable                               | Criterio de Aceptación                                                                      | Esfuerzo Est. |
|------|------------------------------------------|---------------------------------------------------------------------------------------------|---------------|
| 1    | Scrapers + Taxonomía + Tests             | `pytest tests/` al 100%. `bbva.json` y `santander.json` con >100 descuentos. Schema validado. | 3-4 días     |
| 2    | GitHub Actions — Pipeline de datos       | `scrape.yml` ejecuta diariamente sin error. `unified.json` comiteado automáticamente. Rollback funcional. | 1-2 días |
| 3    | SvelteKit Web App                        | Búsqueda full-text funcional. Filtros por categoría, banco, día, tarjeta operativos. Deploy en GH Pages. | 4-5 días |
| 4    | Polish, CI de calidad y lanzamiento      | Lighthouse >90 en Performance y Accessibility. Badge de estado en README. `deploy.yml` en cada push a `main`. | 1-2 días |

---

## 8. Riesgos y Mitigaciones

| # | Riesgo                                                  | Probabilidad | Impacto | Mitigación                                                                                   |
|---|---------------------------------------------------------|:------------:|:-------:|----------------------------------------------------------------------------------------------|
| 1 | **API BBVA rompe estructura de respuesta JSON**         | Media        | Alto    | El campo `raw` preserva la respuesta original. Tests de contrato alertan en CI. Fallback al JSON anterior. |
| 2 | **Santander añade auth a `/bff-benefits`**              | Media        | Alto    | Monitorear headers en cada ejecución. Plan B: scraper con Playwright. |
| 3 | **Rate limiting / bloqueo por IP de GH Actions**        | Baja-Media   | Medio   | Delays de 0.3-0.5s entre requests. Reintentos con backoff exponencial. |
| 4 | **Límite de tamaño del repositorio GitHub**             | Baja         | Medio   | `unified.json` estimado <5 MB. Comprimir si supera 10 MB. Evaluar LFS si el historial crece. |
| 5 | **Datos desactualizados por fallo silencioso del cron** | Baja         | Medio   | Campo `scraped_at` en `unified.json`. El frontend muestra alerta si >25 horas de antigüedad. |
| 6 | **Ambigüedad en mapeo de categorías**                   | Media        | Bajo    | Taxonomía revisada manualmente. Campo `raw` para auditoría. Lista de excepciones en `taxonomy.py`. |

---

## 9. Preguntas Abiertas

1. **Autenticación Santander:** ¿La API `/bff-benefits` requiere token o cookie de sesión desde IP externa no-browser? Requiere prueba empírica con `curl`.

2. **Límite de paginación Santander:** ¿El parámetro `limit` acepta `limit=200` para reducir llamadas? No documentado. Requiere testing.

3. **Cobertura Electro en Santander:** Marcas de tecnología de Santander pueden aparecer bajo `VAR`. El merger debería detectarlas y reclasificarlas a `tecnologia`.

4. **Frecuencia de actualización:** ¿Una ejecución diaria a las 03:00 ART es suficiente? Santander tiene "Súper Miércoles" con promociones que aparecen con menos de 24h de anticipación.

5. **Manejo de promociones expiradas:** ¿Filtrar en el scraper o mostrar con indicador visual de "vencida" en el frontend?

6. **Deduplicación cross-bank:** Una misma cadena (ej. Coto) puede aparecer en ambos bancos con diferentes condiciones. ¿El frontend debe agrupar por `store_name`?

7. **Internacionalización:** El dataset es 100% en español argentino. No se planifica i18n en v1.
