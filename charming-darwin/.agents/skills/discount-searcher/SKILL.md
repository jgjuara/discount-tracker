---
name: discount-searcher
description: Skill para buscar y procesar de forma recurrente descuentos vigentes en la plataforma de beneficios de Banco Santander Argentina.
---

# Skill: discount-searcher

Esta skill permite a los agentes buscar, filtrar, ordenar y reportar promociones y descuentos de Banco Santander Argentina (`https://www.santander.com.ar/personas/beneficios`) a través de la API base `/bff-benefits`.

## Estructura de Endpoints de Referencia
1. **Buscador General:** `GET /bff-benefits/brands`
2. **Catálogo de Categorías:** `GET /bff-benefits/categories?type=[STA|EXC]`
3. **Catálogo de Provincias:** `GET /bff-benefits/provinces`
4. **Detalle de Marca:** `GET /bff-benefits/brands/{id}`

---

## Script Helper de Búsqueda
La skill incluye un script de automatización en Python ubicado en:
`scripts/get_discounts.py`

Este script descarga todas las páginas de resultados usando `curl.exe` del sistema (evitando problemas de bloqueo TLS/SSL nativos en Python), parsea y normaliza los descuentos a valores enteros, identifica comercios especializados en calzado de hombre y genera reportes tanto en JSON como en un archivo Markdown tabulado.

### Parámetros del Script
* `--category`: Código de categoría estándar a buscar (ej. `IND`, `SUP`, `GAS`, `FAR`, `VIA`).
* `--exclusive`: Código de categoría exclusiva a buscar (ej. `SOR`, `SEC`, `MOD`, `SMI`).
* `--days`: Días de la semana separados por comas. Códigos:
  * `0` (Domingo) a `6` (Sábado).
  * `7` (Filtrar por "Hoy").
  * `-1` (Todos los días).
* `--pay-with`: Código de tarjeta o medio de pago:
  * `40` (Tarjeta de Crédito Visa)
  * `41` (Tarjeta de Crédito Mastercard)
  * `42` (Tarjeta de Crédito American Express)
  * `81` (Tarjeta de Débito Visa)
  * `M` (Pagos QR / MODO QR)
* `--location`: Nombre de la provincia (se normaliza automáticamente de forma insensible a mayúsculas/minúsculas y tildes, ej. `CABA`, `Buenos Aires`, `Córdoba`, `Mendoza`).
* `--search`: Palabra clave de búsqueda textual para el nombre de la marca.
* `--output-json`: Ruta absoluta para guardar el resultado crudo en formato JSON.
* `--output-md`: Ruta absoluta para guardar el reporte tabulado en Markdown.
* `--tag-mens-footwear`: Bandera booleana para activar el etiquetado inteligente de comercios conocidos por calzado masculino.
* `--limit`: Cantidad máxima de marcas a retornar por página (por defecto `50`).
* `--retries`: Cantidad de reintentos para las peticiones HTTP en caso de error (por defecto `3`, con backoff exponencial).
* `--config`: Ruta absoluta a un archivo de configuración JSON para personalizar las marcas de calzado masculino y marcas excluidas. Si no se especifica, busca `discount_searcher_config.json` en el directorio del script, y si no existe usa la lista por defecto.
* `--verbose` o `-v`: Activa la salida detallada/depuración para auditar las llamadas a la API, URLs exactas y estados de respuesta.

### Archivo de Configuración (`discount_searcher_config.json`)
El script soporta personalizar el emparejamiento de marcas a través de un archivo JSON con la siguiente estructura:
```json
{
  "mens_footwear_brands": [
    "adidas", "nike", "puma"
  ],
  "exclude_brands": [
    "cheeky", "mimo & co"
  ]
}
```

### Mecanismo de Fallback HTTP y Validación
* **Fallback a urllib:** Si `curl.exe` no se encuentra en el sistema, el script cambia automáticamente a la librería nativa de Python `urllib.request` con cabeceras de navegador configuradas para minimizar bloqueos de red.
* **Validación Rigurosa:** El script valida los parámetros provistos en la línea de comandos contra catálogos reales de la API (categorías válidas, medios de pago válidos, días de la semana y provincias oficiales). Las provincias se normalizan de forma transparente (ej. `"buenos aires"` o `"buenos aires"` -> `"Buenos Aires"`).

---

## Pruebas y Verificación del Script

Para validar que el script funciona correctamente y genera reportes sin errores, ejecute los siguientes comandos de prueba:

1. **Prueba Básica con Salida Detallada y Límite:**
   ```bash
   python "scripts/get_discounts.py" --category SUP --days 3 --location "CABA" --limit 10 --verbose
   ```

2. **Prueba Completa Generando Reportes:**
   ```bash
   python "scripts/get_discounts.py" --category IND --days 1,2 --pay-with 81 --tag-mens-footwear --output-json "reporte.json" --output-md "reporte.md"
   ```

3. **Prueba con Categorías Exclusivas:**
   ```bash
   python "scripts/get_discounts.py" --exclusive SOR --days -1 --verbose
   ```

---

## Instrucciones para el Agente

Cuando el usuario solicite buscar descuentos en la plataforma de Santander, sigue estos pasos:

1. **Identificar Parámetros:** Traduce los filtros indicados por el usuario a los códigos correspondientes:
   * Rubro (Categorías): Indumentaria -> `IND`, Supermercados -> `SUP`, Gastronomía -> `GAS`, Farmacias -> `FAR`.
   * Tarjetas: Visa Crédito -> `40`, Mastercard -> `41`, Amex -> `42`, Débito -> `81`, MODO -> `M`.
   * Provincia: Cotejar contra el catálogo de provincias.
2. **Ejecutar el Script:** Lanza la búsqueda utilizando el script helper provisto. 
   * *Ejemplo para Supermercados con descuento los Miércoles en CABA (límite 20 y reporte MD):*
     ```bash
     python "<workspace_root>/.agents/skills/discount-searcher/scripts/get_discounts.py" --category SUP --days 3 --location "CABA" --limit 20 --output-md "<scratch_dir>/reporte_super.md"
     ```
   * *Ejemplo para Indumentaria con descuento los Lunes y Martes pagando con Débito Visa:*
     ```bash
     python "<workspace_root>/.agents/skills/discount-searcher/scripts/get_discounts.py" --category IND --days 1,2 --pay-with 81 --tag-mens-footwear --output-md "<scratch_dir>/reporte_calzado.md"
     ```
3. **Analizar y Reportar:** 
   * Revisa el archivo Markdown generado.
   * Si es un volumen amplio, guárdalo como un artefacto de conversación en el directorio de la sesión.
   * Presenta un resumen del reporte en español al usuario usando el formato estructurado requerido (Supuestos, Estado de la Información, Contradicciones, Desarrollo y Conclusiones).

