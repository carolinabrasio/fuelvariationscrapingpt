# custom_components/fuelvariationscrapingpt/sensor.py
import logging
import aiohttp
import re
from bs4 import BeautifulSoup
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)
URL = "https://precocombustiveis.pt/proxima-semana/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

SENSORS = ["gasoleo", "gasolina"]


async def fetch_page():
    """Fetch raw HTML from the website."""
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(URL, headers=HEADERS) as resp:
            return await resp.text()

def parse_variation(soup: BeautifulSoup, fuel_type: str):
    """Extrai o texto relevante, a tendencia e a variação do HTML"""

    for h2 in soup.find_all("h2"):
        title = h2.get_text(strip=True).lower()
        p = h2.find_next("p")
        if not p:
            continue

        # Ajusta o texto, separando palavras unidas e removendo espaços extras
        text = re.sub(r'(?<=[a-záéíóú])(?=[A-ZÁÉÍÓÚ])', ' ', p.get_text(strip=False))
        text = re.sub(r'\s+', ' ', text).strip()

        expected_prefix = f"quanto sobe ou desce"
        if fuel_type in title and title.startswith(expected_prefix):
            """Extrai a tendência e a variação em cêntimos/litro do texto."""
            tendencia = "sobe" if "subir" in text.lower() else "desce" if "descer" in text.lower() else "neutro"
            variacao = None

            match = re.search(r"\(([-+]?\d+,\d+)\s*euros?/litro\)", text)
            if match:
                variacao = match.group(1).replace(",", ".")
                try:
                    variacao = float(variacao) * 100  # converte para cêntimos
                except ValueError:
                    variacao = None

            return {
                "texto": text,
                "tendencia": tendencia,
                "variacao": variacao
            }

    return None

def parse_week(soup: BeautifulSoup):
    """Extrai a semana do html"""

    for h1 in soup.find_all("h1"):
        title = h1.get_text(strip=True).lower()

        match = re.search(r"\(\d+\s+a\s+\d+\s+de\s+\w+\)", title)
        if match:
            return match.group(0).strip("()")

    return "atual"

def extract_metric(html: str, fuel_type: str):
    """Extract metric info from the HTML."""

    soup = BeautifulSoup(html, "html.parser")
    metric = parse_variation(soup, fuel_type)

    if metric != None:
        semana = parse_week(soup)
        return {
            "semana": semana,
            "texto": metric["texto"],
            "tendencia": metric["tendencia"],
            "variacao": metric["variacao"]
        }

    return None

async def async_setup_platform(hass, config, async_add_entities: AddEntitiesCallback, discovery_info=None):
    sensors = [FuelVariationSensor(fuel_type) for fuel_type in SENSORS]
    async_add_entities(sensors, True)


class FuelVariationSensor(SensorEntity):
    def __init__(self, fuel_type):
        self._fuel_type = fuel_type
        self._name = f"Variação do preço {fuel_type.capitalize()}"
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"fuel_variation_{self._fuel_type}"

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        try:
            html = await fetch_page()
            parsed = extract_metric(html, self._fuel_type)
            if parsed:
                self._state = parsed["texto"]
                self._attributes = {
                    "semana": parsed["semana"],
                    "tendencia": parsed["tendencia"],
                    "variacao_cent_litro": parsed["variacao"],
                }
        except Exception as e:
            _LOGGER.error("Erro ao buscar preços de %s: %s", self._fuel_type, e)
            self._state = None
            self._attributes = {}
