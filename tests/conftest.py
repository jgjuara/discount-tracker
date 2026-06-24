import pytest


# ---------------------------------------------------------------------------
# BBVA fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def bbva_list_response():
    """Matches the BBVA /communications schema with 2 sample promos."""
    return {
        "code": 0,
        "message": "Comunicaciones: 2   paginas: 1",
        "data": [
            {
                "id": "85443",
                "imagen": "https://go.bbva.com.ar/fgo/sites/default/files/imagen/comercio/zara.png",
                "cabecera": "Zara 3 cuotas",
                "subcabecera": "Hasta 3 cuotas sin interes. Válida del 01-06-2026 al 30-06-2026",
                "idCampania": "",
                "esCampania": False,
                "fechaDesde": "2026-06-01",
                "fechaHasta": "2026-06-30",
                "diasPromo": "1,1,1,1,1,1,1",
                "montoTope": None,
                "grupoTarjeta": "Tarjetas de crédito BBVA",
            },
            {
                "id": "85444",
                "imagen": "https://go.bbva.com.ar/fgo/sites/default/files/imagen/comercio/nike.png",
                "cabecera": "Nike 30% de reintegro",
                "subcabecera": "30% de reintegro con tarjetas BBVA. Válida del 01-06-2026 al 30-06-2026",
                "idCampania": "",
                "esCampania": False,
                "fechaDesde": "2026-06-01",
                "fechaHasta": "2026-06-30",
                "diasPromo": "1,1,1,1,1,1,1",
                "montoTope": 5000,
                "grupoTarjeta": "Tarjetas de crédito BBVA",
            },
        ],
    }


@pytest.fixture
def bbva_empty_list_response():
    """Matches the BBVA /communications schema with empty data (end of pagination)."""
    return {
        "code": 0,
        "message": "Comunicaciones: 0   paginas: 0",
        "data": [],
    }


@pytest.fixture
def bbva_detail_response():
    """Matches the BBVA /communication/{id} schema."""
    return {
        "code": 0,
        "message": "comunicaciones: 1      paginas: 1",
        "data": {
            "id": "85443",
            "imagen": "https://go.bbva.com.ar/fgo/sites/default/files/imagen/comercio/zara.png",
            "cabecera": "Zara 3 cuotas",
            "beneficios": [
                {
                    "cuota": 3,
                    "tope": None,
                    "tipoTope": " ",
                    "frecuenciaTope": " ",
                    "requisitos": ["Con tus tarjetas de crédito BBVA"],
                }
            ],
            "canalesVenta": {
                "sucursales": [
                    {
                        "direccion": "Guemes 897",
                        "localidad": "Avellaneda",
                        "latitude": "-34.6924055",
                        "longitude": "-58.387320",
                    }
                ],
                "web": [{"name": "Zara", "url": "https://zara.com/ar"}],
            },
            "basesCondiciones": "PROMOCIÓN VÁLIDA PARA CLIENTES QUE ABONEN SUS COMPRAS EN HASTA 3 CUOTAS...",
            "diasPromo": "1,1,1,1,1,1,1",
            "vigencia": "Del 01/06/2026 hasta 30/06/2026",
            "grupoTarjeta": "Tarjetas de crédito BBVA",
            "tiempoAcreditacion": None,
            "esModo": False,
        },
    }


# ---------------------------------------------------------------------------
# Santander fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def santander_brands_response():
    """Matches the Santander /bff-benefits/brands schema with 2 sample brands."""
    return {
        "brands": [
            {
                "id": 2763,
                "name": "Nike",
                "logo": "https://www.santander.com.ar/assets/brand/nike.png",
                "categories": ["DEP", "IND"],
            },
            {
                "id": 1042,
                "name": "Coto",
                "logo": "https://www.santander.com.ar/assets/brand/coto.png",
                "categories": ["SUP"],
            },
        ],
        "total": 2,
        "page": 1,
        "limit": 16,
    }


@pytest.fixture
def santander_empty_brands_response():
    """Empty brands page — signals end of pagination."""
    return {
        "brands": [],
        "total": 0,
        "page": 2,
        "limit": 16,
    }


@pytest.fixture
def santander_brand_detail_response():
    """Matches the Santander /bff-benefits/brands/{id} schema."""
    return {
        "id": 2763,
        "name": "Nike",
        "logo": "https://www.santander.com.ar/assets/brand/nike.png",
        "publications": [
            {
                "id": "sant-nike-30",
                "title": "30% de descuento",
                "description": "30% de descuento en toda la tienda Nike con tarjeta Mastercard.",
                "customerDiscount": 30,
                "interestFreeFees": True,
                "initialQuote": 3,
                "finalQuote": 6,
                "monday": True,
                "tuesday": True,
                "wednesday": True,
                "thursday": True,
                "friday": True,
                "saturday": True,
                "sunday": True,
                "fullWeek": True,
                "categories": ["DEP", "IND"],
                "legal": "Válido del 01/06/2026 al 30/06/2026. Tope $5.000.",
                "payWith": [41],
            }
        ],
    }
