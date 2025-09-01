# custom_components/fuel_variation_scraping/sensor.py
import logging
import aiohttp
import re
from bs4 import BeautifulSoup
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .parse import parse_variation  # <-- import do seu parse.py

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


def extract_variation(html: str, fuel_type: str):
    """Extract fuel variation info from the HTML."""
    soup = BeautifulSoup(html, "html.parser")
    for h2 in soup.find_all("h2"):
        title = h2.get_text(strip=True).lower()
        p = h2.find_next("p")
        if not p:
            continue
        # Ajusta o texto, separando palavras unidas e removendo espaços extras
        text = re.sub(r'(?<=[a-záéíóú])(?=[A-ZÁÉÍÓÚ])', ' ', p.get_text(strip=True))
        text = re.sub(r'\s+', ' ', text).strip()

        expected_prefix = f"quanto sobe ou desce o {fuel_type}"
        if title.startswith(expected_prefix):
            return parse_variation(text)  # usa a função do parse.py

    return None


async def async_setup_platform(hass, config, async_add_entities: AddEntitiesCallback, discovery_info=None):
    sensors = [FuelVariationSensor(fuel_type) for fuel_type in SENSORS]
    async_add_entities(sensors, True)


class FuelVariationSensor(SensorEntity):
    def __init__(self, fuel_type):
        self._fuel_type = fuel_type
        self._name = f"Preço {fuel_type.capitalize()}"
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
            parsed = extract_variation(html, self._fuel_type)
            if parsed:
                self._state = parsed["texto"]
                self._attributes = {
                    "tendencia": parsed["tendencia"],
                    "variacao_eur_litro": parsed["variacao"],
                }
        except Exception as e:
            _LOGGER.error("Erro ao buscar preços de %s: %s", self._fuel_type, e)
            self._state = None
            self._attributes = {}
