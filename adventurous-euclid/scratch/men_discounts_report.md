# Reporte de Promociones de Moda y Accesorios (BBVA Go - Rubro 170)

Este reporte consolida y clasifica las promociones del rubro 170 de la API de BBVA Go filtradas para hombres en las categorías de **Ropa de hombres** y **Calzado de hombres**, ordenadas de mayor a menor descuento.

## Supuestos y Consideraciones
- Se descargaron las promociones desde `pager=0` hasta agotar las páginas de resultados de la API de BBVA Go (hasta `pager=16`).
- Para determinar el porcentaje de descuento y las cuotas sin interés se analizaron los campos `cabecera` y `subcabecera` usando expresiones regulares.
- Las marcas generales (como Zara, Nike, Vans, Topper, Dexter, Moov, Grid, Stock Center, Adidas, Puma, The North Face, Pampero, Decathlon, etc.) y las tiendas de deportes (identificadas por patrones como 'sport' o 'deport') que comercializan tanto indumentaria como calzado fueron clasificadas en ambas categorías, a menos que las palabras clave de la promoción restringieran su aplicación a una sola categoría.
- Las promociones se ordenaron de mayor a menor descuento, priorizando el porcentaje de reintegro y secundariamente el número de cuotas sin interés.

## Resumen Estadístico
- **Total de promociones analizadas (Rubro 170):** 336
- **Clasificadas como Ropa de Hombres:** 54
- **Clasificadas como Calzado de Hombres:** 50
- **Promociones omitidas (ópticas, joyerías, locales de mujer/niños):** 260

## Destacados (Mejores Descuentos)
### Mejor Promoción en Ropa de Hombres
- **Comercio:** Ubatuba 30% y 6 cuotas
- **Detalle:** 30% y 6 cuotas sin interés .Promoción válida desde 07-01-2026 hasta 30-06-2026
- **Descuento:** 30% | **Cuotas:** 6

### Mejor Promoción en Calzado de Hombres
- **Comercio:** Las Juanas Calzados 30% y 6 cuotas
- **Detalle:** 30% y 6 cuotas sin interés .Promoción válida desde 06-05-2026 hasta 30-06-2026
- **Descuento:** 30% | **Cuotas:** 6

## Detalle de Promociones por Categoría (Top 15)

### Ropa de Hombres (Top 15)
| Comercio / Cabecera | Detalle / Subcabecera | Reintegro (%) | Cuotas |
| --- | --- | :---: | :---: |
| Ubatuba 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 07-01-2026 hasta 30-06-2026 | 30% | 6 |
| Kevingston 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 10-06-2026 hasta 30-06-2026 | 30% | 6 |
| Genoa Sweaters 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 15-04-2026 hasta 30-06-2026 | 30% | 6 |
| Albert Sport 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 06-05-2026 hasta 30-06-2026 | 30% | 6 |
| Albert Sport 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 14-01-2026 hasta 30-06-2026 | 30% | 6 |
| Ubatuba 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 11-03-2026 hasta 30-06-2026 | 30% | 6 |
| Real Sport 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 03-06-2026 hasta 30-06-2026 | 30% | 6 |
| Genoa Sweaters 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 29-04-2026 hasta 30-06-2026 | 30% | 6 |
| Vincenzo Collezione 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 07-01-2026 hasta 30-06-2026 | 30% | 6 |
| Vincenzo Collezione 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 07-01-2026 hasta 30-06-2026 | 30% | 6 |
| Pampero -rosario- 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 07-01-2026 hasta 30-06-2026 | 30% | 6 |
| Vincenzo Collezione 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 07-01-2026 hasta 30-06-2026 | 30% | 6 |
| Vincenzo Collezione 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 07-01-2026 hasta 30-06-2026 | 30% | 6 |
| Deport Show 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 03-06-2026 hasta 30-06-2026 | 30% | 6 |
| Now Sport 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 07-01-2026 hasta 30-06-2026 | 30% | 6 |

### Calzado de Hombres (Top 15)
| Comercio / Cabecera | Detalle / Subcabecera | Reintegro (%) | Cuotas |
| --- | --- | :---: | :---: |
| Las Juanas Calzados 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 06-05-2026 hasta 30-06-2026 | 30% | 6 |
| Albert Sport 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 06-05-2026 hasta 30-06-2026 | 30% | 6 |
| Moon Calzados 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 27-05-2026 hasta 30-06-2026 | 30% | 6 |
| Tosone Zapatos 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 03-06-2026 hasta 30-06-2026 | 30% | 6 |
| Albert Sport 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 14-01-2026 hasta 30-06-2026 | 30% | 6 |
| Real Sport 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 03-06-2026 hasta 30-06-2026 | 30% | 6 |
| Jm Shoes 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 31-03-2026 hasta 30-06-2026 | 30% | 6 |
| Start Calzados 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 03-06-2026 hasta 30-06-2026 | 30% | 6 |
| Pampero -rosario- 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 07-01-2026 hasta 30-06-2026 | 30% | 6 |
| Calzados Mario 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 20-05-2026 hasta 30-06-2026 | 30% | 6 |
| Niko Calzados 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 03-06-2026 hasta 30-06-2026 | 30% | 6 |
| Deport Show 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 03-06-2026 hasta 30-06-2026 | 30% | 6 |
| Now Sport 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 07-01-2026 hasta 30-06-2026 | 30% | 6 |
| Valentino Calzados 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 11-03-2026 hasta 30-06-2026 | 30% | 6 |
| Capitan Hockey 30% y 6 cuotas | 30% y 6 cuotas sin interés .Promoción válida desde 07-01-2026 hasta 30-06-2026 | 30% | 6 |
