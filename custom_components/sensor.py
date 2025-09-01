import logging
import aiohttp
import re
from bs4 import BeautifulSoup
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)
URL = "https://precocombustiveis.pt/proxima-semana/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0.0.1 Safari/537.36"
}

SENSORS = ["gasoleo", "gasolina"]

async def async_setup_platform(hass, config, async_add_entities: AddEntitiesCallback, discovery_info=None):
    """Setup the fuel variation sensors."""
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
        """Fetch the latest data from the website using aiohttp with 30s timeout."""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(URL, headers=HEADERS) as resp:
                    html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")

            for h2 in soup.find_all("h2"):
                title = h2.get_text(strip=True).lower()
                p = h2.find_next("p")
                if not p:
                    continue
                text = p.get_text(strip=True)

                # Normaliza espaços e separa palavras coladas
                text = re.sub(r'(?<=[a-záéíóú])(?=[A-ZÁÉÍÓÚ])', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()

                if self._fuel_type in title:
                    parsed = self.parse_variation(text)
                    self._state = parsed["texto"]
                    self._attributes = {
                        "tendencia": parsed["tendencia"],
                        "variacao_eur_litro": parsed["variacao"]
                    }
                    break

        except Exception as e:
            _LOGGER.error("Erro ao buscar preços de %s: %s", self._fuel_type, e)
            self._state = None
            self._attributes = {}

    @staticmethod
    def parse_variation(text: str):
        """Extrai tendencia e variação em euros/litro do texto."""
        tendencia = "sobe" if "subir" in text.lower() else "desce" if "descer" in text.lower() else "neutro"
        variacao = None

        match = re.search(r"\(([-+]?\d+,\d+)\s*euros?/litro\)", text)
        if match:
            variacao = match.group(1).replace(",", ".")
            try:
                variacao = float(variacao)
            except ValueError:
                variacao = None

        return {
            "texto": text,
            "tendencia": tendencia,
            "variacao": variacao
        }

