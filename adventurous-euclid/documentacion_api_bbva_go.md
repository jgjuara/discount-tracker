# Documentación Técnica de la API de BBVA Go Argentina

Esta documentación detalla los hallazgos técnicos derivados de la investigación de la API privada que da soporte al portal de beneficios **BBVA Go Argentina** (`go.bbva.com.ar`).

---

## 1. Información General y Autenticación

* **URL Base:** `https://go.bbva.com.ar/willgo/fgo/API/v3`
* **Protocolo:** HTTPS
* **Autenticación:** No requiere credenciales ni tokens de autorización dinámicos (Bearer/Basic). Sin embargo, la API valida estrictamente los encabezados de la petición para evitar accesos no autorizados.

### Encabezados Requeridos (Headers)
Para realizar peticiones exitosas y evitar bloqueos por parte del servidor web (HTTP 403 o 400), se deben enviar los siguientes encabezados:

| Encabezado | Valor de Referencia |
| :--- | :--- |
| `user-agent` | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...` |
| `accept-language` | `es-AR,es-US;q=0.9,es;q=0.8` |
| `origin` | `https://www.bbva.com.ar` |
| `referer` | `https://www.bbva.com.ar/` |
| `accept` | `*/*` |

---

## 2. Catálogo de Endpoints

### A. Listar Promociones
* **Ruta:** `/communications`
* **Método:** `GET`
* **Descripción:** Devuelve un listado paginado de promociones que coinciden con los rubros especificados.
* **Parámetros de Consulta (Query Params):**
  * `pager` (Requerido - Entero): Índice de página que comienza en `0`. Cada página contiene un máximo de **20 elementos**.
  * `rubros` (Requerido - String): Uno o más IDs de rubros separados por comas (ej. `rubros=170` o `rubros=170,26`).

### B. Detalle de Promoción
* **Ruta:** `/communication/{id}`
* **Método:** `GET`
* **Descripción:** Devuelve la información extendida, sucursales físicas geolocalizadas y bases y condiciones de una promoción específica.
* **Parámetros de Ruta:**
  * `id` (Requerido - String): ID único de la promoción (ej. `85443`).

### C. Endpoints Inexistentes (404 Not Found)
Las siguientes rutas teóricas fueron testeadas y se confirmó que **no existen** en el servidor de la API:
* `/rubros`
* `/categories`
* `/filters`
* `/config`
* `/subrubros`
* `/communications/{id}` (la versión pluralizada con ID en ruta retorna 404)

---

## 3. Mapeo de Rubros (Categorías de Consumo)

A través de un barrido sistemático (IDs 1 a 300), se identificaron **12 rubros activos** en la API que consolidan un total de **1,284 promociones vigentes**:

| ID de Rubro | Nombre de la Categoría | Cantidad de Promos | Ejemplos de Comercios y Beneficios |
| :---: | :--- | :---: | :--- |
| **3** | Gastronomía | 270 | *Farinelli* (20% reintegro), *Casa Saenz* (20% reintegro) |
| **4** | Entretenimiento / Espectáculos | 48 | *Rocky* (30% + 3 cuotas), *Disney On Ice* (6 cuotas) |
| **8** | Cuidado Personal / Farmacias | 83 | *Farmaonline* (10% + 3 cuotas), *Parfumerie* (10% + 6 cuotas) |
| **13** | Turismo / Viajes | 9 | *Assist Card* (12 cuotas), *Duty Free Shop* (20% reintegro) |
| **26** | Supermercados | 88 | *Coto* (30% descuento), *Kilbel* (20% reintegro MODO) |
| **170** | Moda y Accesorios | 336 | *Zara* (3 cuotas), *Sarkany* (20% + 6 cuotas), *Nike* (6 cuotas) |
| **173** | Hogar, Construcción y Decoración | 138 | *Oscar Barbieri* (12 cuotas), *Rouge Maison* (10%) |
| **174** | Automotores (Servicios y repuestos) | 41 | *Subaru* (12 cuotas), *Norauto* (6 cuotas) |
| **175** | Jugueterías / Niños | 39 | *Kinderland* (10% + 3 cuotas), *Cebra* (20% + 3 cuotas) |
| **184** | Deportes, Gimnasios y Educación | 19 | *River Plate Instituto* (10%), *Megatlon* (15% + 12 cuotas) |
| **192** | Electro y Tecnología | 137 | *Bringeri Hogar* (12 cuotas), *Jumbo Electro* (20% MODO) |
| **195** | Bazar, Regalos y Vinos | 54 | *Bonvivir* (20% descuento), *Frappé* (30% descuento) |

---

## 4. Esquemas de Datos (JSON)

### A. Respuesta de `/communications` (Lista)
```json
{
  "code": 0,
  "message": "Comunicaciones: 336   paginas: 17",
  "data": [
    {
      "id": "85443",
      "imagen": "https://go.bbva.com.ar/fgo/sites/default/files/imagen/comercio/19275_zara_311x208.png",
      "cabecera": "Zara 3 cuotas",
      "subcabecera": "Hasta 3 cuotas sin interes .Promoción válida desde 01-06-2026 hasta 30-06-2026",
      "idCampania": "",
      "esCampania": false,
      "fechaDesde": "2026-06-01",
      "fechaHasta": "2026-06-30",
      "diasPromo": "1,1,1,1,1,1,1",
      "montoTope": null,
      "grupoTarjeta": "Tarjetas de crédito BBVA"
    }
  ]
}
```

### B. Respuesta de `/communication/{id}` (Detalle)
```json
{
  "code": 0,
  "message": "comunicaciones: 1      paginas: 1",
  "data": {
    "id": "85443",
    "imagen": "https://go.bbva.com.ar/fgo/sites/default/files/imagen/comercio/19275_zara_311x208.png",
    "cabecera": "Zara 3 cuotas",
    "beneficios": [
      {
        "cuota": 3,
        "tope": null,
        "tipoTope": " ",
        "frecuenciaTope": " ",
        "requisitos": [
          "Con tus tarjetas de crédito BBVA"
        ]
      }
    ],
    "canalesVenta": {
      "sucursales": [
        {
          "direccion": "Guemes 897",
          "localidad": "Avellaneda",
          "latitude": "-34.6924055",
          "longitude": "-58.38732060000001"
        }
      ],
      "web": [
        {
          "name": "Zara",
          "url": "https://zara.com/ar"
        }
      ]
    },
    "basesCondiciones": "PROMOCIÓN VÁLIDA PARA CLIENTES QUE ABONEN SUS COMPRAS EN HASTA 3 CUOTAS...",
    "diasPromo": "1,1,1,1,1,1,1",
    "vigencia": "Del 01/06/2026 hasta 30/06/2026",
    "grupoTarjeta": "Tarjetas de crédito BBVA",
    "tiempoAcreditacion": null,
    "esModo": false
  }
}
```

---

## 5. Comportamiento en Casos Límite y Errores de Validación

Se verificó la robustez de la API en el parámetro de paginación `pager`:

1. **Páginas fuera de rango superior (ej. `pager=17` cuando el máximo es 16):** Retorna un código HTTP `200 OK` con un arreglo `data` vacío (`[]`).
2. **Páginas negativas (ej. `pager=-1`):** Produce un error HTTP `500 Internal Server Error` debido a fallas de conversión interna del backend.
3. **Parámetro no numérico (ej. `pager=abc`):** Produce igualmente un error HTTP `500 Internal Server Error`.

---

## 6. Limitaciones del Endpoint `/communications`

Durante las pruebas se evaluaron múltiples parámetros para búsqueda de texto libre, filtrado regional u ordenamiento (`q`, `query`, `search`, `texto`, `provincia`, `sort`, `orden`).

**Resultado:** Todos estos parámetros son **ignorados por completo** por el backend de la API. Las promociones retornadas bajo `/communications` se filtran únicamente mediante el parámetro `rubros`. Esto indica que la búsqueda por texto o geolocalización en la aplicación móvil de BBVA Go se realiza **del lado del cliente (frontend)** filtrando el subset JSON recibido, o bien que existe un endpoint de búsqueda independiente (no mapeado en la URL base pública).
