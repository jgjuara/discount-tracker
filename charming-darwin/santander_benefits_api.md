# Documentación de la API de Beneficios de Santander

Esta documentación describe el funcionamiento y estructura de la API utilizada por el portal de beneficios de Banco Santander Argentina (`https://www.santander.com.ar/personas/beneficios`).

La API opera bajo el prefijo base `/bff-benefits` y sirve tanto para obtener catálogos como para realizar búsquedas avanzadas y filtrados de promociones.

---

## 1. Endpoints de Catálogo

### 1.1. Categorías (`GET /bff-benefits/categories`)
Este endpoint retorna el listado de categorías disponibles. Soporta un parámetro de consulta `type` para clasificar las categorías.

* **Parámetros de consulta:**
  * `type` (requerido):
    * `STA` (Standard): Categorías generales del negocio.
    * `EXC` (Exclusive): Beneficios o programas especiales de suscripción.

#### Categorías Estándar (`type=STA`)
| Código | Descripción | Tipo |
| :--- | :--- | :--- |
| `AUT` | Automotor | STA |
| `DEP` | Deporte | STA |
| `DIN` | Dining | STA |
| `EDU` | Formación | STA |
| `ESP` | Espectáculos | STA |
| `FAR` | Farmacias | STA |
| `GAS` | Gastronomía | STA |
| `HOG` | Hogar | STA |
| `IND` | Indumentaria | STA |
| `JUG` | Infantiles | STA |
| `LIB` | Librerías | STA |
| `PELU` | Peluquerías | STA |
| `PER` | Perfumerías | STA |
| `SUP` | Supermercados | STA |
| `VAR` | Varios | STA |
| `VIA` | Viajes | STA |

#### Categorías Exclusivas (`type=EXC`)
| Código | Descripción | Tipo |
| :--- | :--- | :--- |
| `CPE` | Cuidado personal | EXC |
| `MOD` | Modo | EXC |
| `SEC` | Select | EXC |
| `SMI` | Súper Miércoles | EXC |
| `SOR` | Sorpresa | EXC |

---

### 1.2. Provincias (`GET /bff-benefits/provinces`)
Retorna el catálogo completo de las provincias de Argentina, incluyendo identificadores, nombres oficiales y coordenadas geográficas de referencia (latitud y longitud).

#### Listado de Provincias
| ID | Nombre (`location` value) | Latitud | Longitud |
| :-: | :--- | :-: | :-: |
| `24` | `CABA` | `-34.6037` | `-58.3816` |
| `1` | `Buenos Aires` | `-34.6100` | `-58.3800` |
| `2` | `Catamarca` | `-28.4694` | `-65.7850` |
| `3` | `Chaco` | `-26.9927` | `-60.9965` |
| `4` | `Chubut` | `-45.7919` | `-67.8957` |
| `5` | `Córdoba` | `-31.4201` | `-64.1888` |
| `6` | `Corrientes` | `-27.4805` | `-58.8349` |
| `7` | `Entre Ríos` | `-32.0322` | `-60.6953` |
| `8` | `Formosa` | `-26.1742` | `-58.1816` |
| `9` | `Jujuy` | `-24.1855` | `-65.2995` |
| `10` | `La Pampa` | `-36.6168` | `-64.2945` |
| `11` | `La Rioja` | `-29.4144` | `-66.8509` |
| `12` | `Mendoza` | `-32.8894` | `-68.8458` |
| `13` | `Misiones` | `-26.5703` | `-54.5882` |
| `14` | `Neuquén` | `-38.9516` | `-67.9614` |
| `15` | `Río Negro` | `-39.0333` | `-63.0011` |
| `16` | `Salta` | `-24.7850` | `-65.4115` |
| `17` | `San Juan` | `-31.5375` | `-68.5365` |
| `18` | `San Luis` | `-33.2956` | `-66.3354` |
| `19` | `Santa Cruz` | `-50.0158` | `-68.1193` |
| `20` | `Santa Fe` | `-31.6333` | `-60.7003` |
| `21` | `Santiago del Estero` | `-29.9332` | `-63.5860` |
| `22` | `Tierra del Fuego` | `-54.8019` | `-68.1193` |
| `23` | `Tucumán` | `-26.8176` | `-65.2170` |

---

## 2. Endpoint de Búsqueda y Filtrado (`GET /bff-benefits/brands`)

Este es el endpoint principal utilizado para listar las marcas que poseen promociones vigentes. Admite múltiples parámetros para filtrar los resultados.

### Parámetros de Consulta (Query Parameters)

| Parámetro | Tipo | Descripción | Ejemplo / Valores válidos |
| :--- | :--- | :--- | :--- |
| `search` | String | Filtro por nombre o palabra clave de la marca. Búsqueda insensible a mayúsculas/minúsculas. | `search=Nike` |
| `categories` | String | Códigos de categorías estándar (`STA`). Admite múltiples valores separados por comas (operación OR). | `categories=SUP` (Supermercados)<br>`categories=SUP,IND` (Super o Indumentaria) |
| `exclusive` | String | Código de categoría exclusiva (`EXC`). Filtra marcas pertenecientes a un programa especial. | `exclusive=SOR` (Sorpresa)<br>`exclusive=SEC` (Select)<br>`exclusive=MOD` (Modo)<br>`exclusive=SMI` (Súper Miércoles) |
| `days` | String/Int | Día(s) de la semana en que está activa la promoción. Admite múltiples valores separados por comas (operación OR). | `0` (Domingo) a `6` (Sábado)<br>`7` (Hoy - dynamic)<br>`-1` (Todos los días / Every day)<br>`days=1,2` (Lunes o Martes) |
| `pay_with` | String | Código del medio de pago o tarjeta requerido para el beneficio. | `40` (Crédito Visa)<br>`41` (Mastercard)<br>`42` (American Express)<br>`43` (Recargable Visa)<br>`81` (Débito Visa)<br>`M` (QR / MODO QR) |
| `location` | String | Nombre exacto de la provincia o localidad (debe coincidir con el campo `name` del catálogo de provincias). | `location=CABA`<br>`location=Buenos Aires` |
| `page` | Integer | Número de página para la paginación de resultados (1-indexed). | `page=1` |
| `limit` | Integer | Cantidad máxima de marcas a retornar por página. Por defecto es `16` si no se especifica. | `limit=12` |

---

## 3. Endpoint de Detalle de Marca (`GET /bff-benefits/brands/{id}`)

Retorna la lista de promociones o publicaciones específicas asociadas a una marca identificada por su ID único.

* **Estructura del Path:** `/bff-benefits/brands/{id_de_la_marca}`
  * Ejemplo: `GET /bff-benefits/brands/2763` (Nike).

### Estructura de la Respuesta (Publicaciones)
Cada publicación contiene el detalle del descuento:
* **Campos booleanos de días:** `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday` y `fullWeek` detallan los días específicos de vigencia.
* `customerDiscount`: Porcentaje numérico del beneficio (ej. `30` para 30% de ahorro).
* `interestFreeFees`: Booleano que indica si incluye cuotas sin interés.
* `initialQuote` / `finalQuote`: Rango de cuotas disponibles (ej. de 2 a 9 cuotas).
* `texts`: Objeto con el título resumido (`title`) y descripción corta (`description`).
* `legal`: Texto legal completo con las condiciones, vigencia y exclusiones de la promoción.
* `categories`: Array de categorías a las que aplica (ej. `DEP`, `IND`).

---

## 4. Ejemplos de Casos de Uso y Consultas a la API

### Caso A: Buscar promociones de Supermercados activas los días Lunes
* **URL:** `GET /bff-benefits/brands?categories=SUP&days=1&limit=12`
* **Comportamiento:** Filtra marcas de categoría `SUP` (Supermercados) que tengan promociones vigentes el lunes (código `1`).

### Caso B: Buscar marcas que acepten tarjeta Mastercard (código 41) en la provincia de Córdoba
* **URL:** `GET /bff-benefits/brands?pay_with=41&location=C%C3%B3rdoba&limit=12`
* **Comportamiento:** Retorna marcas con promociones usando tarjeta Mastercard dentro de la provincia de Córdoba.

### Caso C: Buscar promociones del programa "Sorpresa" activas los fines de semana (Sábado y Domingo)
* **URL:** `GET /bff-benefits/brands?exclusive=SOR&days=0,6&limit=12`
* **Comportamiento:** Retorna marcas adheridas al programa exclusivo Sorpresa (`exclusive=SOR`) cuyos beneficios estén activos el domingo (`0`) o el sábado (`6`).

### Caso D: Búsqueda textual por marca ("Nike")
* **URL:** `GET /bff-benefits/brands?search=Nike`
* **Comportamiento:** Retorna únicamente las marcas cuyo nombre coincide parcialmente o totalmente con "Nike".
