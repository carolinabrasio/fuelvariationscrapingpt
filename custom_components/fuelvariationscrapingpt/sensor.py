# custom_components/fuelvariationscrapingpt/sensor.py
import logging
import aiohttp
import re
from bs4 import BeautifulSoup
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)
URL = "https://precocombustiveis.pt/proxima-semana/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Adiciona um intervalo de 6 horas entre atualizações
SCAN_INTERVAL = timedelta(hours=6)
SENSORS = ["gasoleo", "gasolina"]
MAP = {"gasoleo": "gasóleo", "gasolina": "gasolina"}

async def fetch_page():
    """Fetch raw HTML from the website."""
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(URL, headers=HEADERS) as resp:
            return await resp.text()

def parse_variation(soup: BeautifulSoup, fuel_type: str):
    """Extrai o texto relevante, a tendencia e a variação do HTML"""

    for h3 in soup.find_all("h3"):
        title = h3.get_text(strip=True).lower()
        p = h3.find_next("p")
        if not p:
            continue

        # Ajusta o texto, separando palavras unidas e removendo espaços extras
        text = re.sub(r'(?<=[a-záéíóú])(?=[A-ZÁÉÍÓÚ])', ' ', p.get_text(strip=False))
        text = re.sub(r'\s+', ' ', text).strip()

        expected_prefix = f"sobe ou desce na próxima semana"
        fuel_name = MAP[fuel_type]
        if fuel_name in title and title.endswith(expected_prefix):
            """Extrai a tendência e a variação em cêntimos/litro do texto."""
            variacao = None
            variacao_em_cent = None

            match = re.search(r"(.?\d+,\d+)\s?€/l", text, re.IGNORECASE)
            if match:
                variacao = match.group(1).replace(",", ".").replace('−', '-')
                try:
                    variacao = float(variacao)
                    variacao_em_cent = variacao * 100  # converte para cêntimos
                except ValueError:
                    variacao = None
                    variacao_em_cent = None

            if variacao_em_cent is None:
                tendencia = "neutro"
                variation_level = "ligeira"
            else:
                tendencia = "sobe" if variacao_em_cent > 0 else "desce" if variacao_em_cent < 0 else "neutro"
                variation_level = "forte" if abs(variacao_em_cent) >= 6 else "moderada" if abs(variacao_em_cent) >= 2 else "ligeira"

            preco_referencia = get_avg_price(soup, fuel_type)
            final_price = preco_referencia + variacao if (preco_referencia is not None and variacao is not None) else None

            return {
                "texto": text,
                "tendencia": tendencia,
                "variacao": variacao_em_cent,
                "nivel_de_variacao": variation_level,
                "preco_referencia": preco_referencia,
                "preco_final": final_price,
            }

    return None

def parse_week(soup: BeautifulSoup, updated_date: str):
    """Extrai a semana do html"""

    data = datetime.strptime(updated_date, "%Y-%m-%d")
    next_monday = data + timedelta(days=(7 - data.weekday()) % 7)
    next_sunday = next_monday + timedelta(days=6)

    return {
        "start": next_monday.strftime("%Y-%m-%d"),
        "end": next_sunday.strftime("%Y-%m-%d")
    }

def parse_update_date(soup: BeautifulSoup):
    """Extrai a data da última atualização da página do html"""

    last_updated = soup.find("time")

    if last_updated != None:
        return last_updated['datetime']

    return None

def get_avg_price(soup: BeautifulSoup, fuel_type: str):
    """Extrai o preço médio de referência do html"""

    section = soup.find(id="referencia")

    if section != None:
        p = section.find("p")
        normalized_p = p.get_text(strip=True).lower()
        fuel_name = MAP[fuel_type]
        match = re.search(r"preço de referência.*(\d+,\d+).*" + re.escape(fuel_name) + r" simples", normalized_p, re.IGNORECASE)
        if match:
            preco_referencia = match.group(1).replace(",", ".").replace('−', '-')
            return float(preco_referencia)

    return None

def extract_metric(html: str, fuel_type: str):
    """Extract metric info from the HTML."""

    soup = BeautifulSoup(html, "html.parser")
    metric = parse_variation(soup, fuel_type)

    if metric != None:
        last_updated = parse_update_date(soup)
        semana = parse_week(soup, last_updated)
        metric = {
            "inicio_previsao": semana["start"],
            "fim_previsao": semana["end"],
            "atualizacao": last_updated,
            "texto": metric["texto"],
            "tendencia": metric["tendencia"],
            "variacao": metric["variacao"],
            "nivel_de_variacao": metric["nivel_de_variacao"],
            "preco_referencia": metric["preco_referencia"],
            "preco_final": metric["preco_final"],
        }
        calc_impact(metric)
        return metric

    return None

def calc_impact(metric: dict):
    """Calcula o impacto por tanque com base na variação prevista e no preço de referência"""

    final_price = metric["preco_final"]
    ref_price = metric["preco_referencia"]
    varicao = metric["variacao"]

    if final_price != None and ref_price != None:
        metric["impacto_40l"] = round((final_price - ref_price) * 40, 3)
        metric["impacto_50l"] = round((final_price - ref_price) * 50, 3)
        metric["impacto_60l"] = round((final_price - ref_price) * 60, 3)
        metric["preco_final_40l"] = round(final_price * 40, 3)
        metric["preco_final_50l"] = round(final_price * 50, 3)
        metric["preco_final_60l"] = round(final_price * 60, 3)
        metric["preco_atual_40l"] = round(ref_price * 40, 3)
        metric["preco_atual_50l"] = round(ref_price * 50, 3)
        metric["preco_atual_60l"] = round(ref_price * 60, 3)

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
                    "inicio_previsao": parsed["inicio_previsao"],
                    "fim_previsao": parsed["fim_previsao"],
                    "ultima_atualizacao": parsed["atualizacao"],
                    "tendencia": parsed["tendencia"],
                    "variacao_cent_litro": parsed["variacao"],
                    "nivel_de_variacao": parsed["nivel_de_variacao"],
                    "preco_referencia": parsed["preco_referencia"],
                    "preco_final": parsed["preco_final"],
                    "impacto_40l": parsed.get("impacto_40l"),
                    "impacto_50l": parsed.get("impacto_50l"),
                    "impacto_60l": parsed.get("impacto_60l"),
                    "preco_final_40l": parsed.get("preco_final_40l"),
                    "preco_final_50l": parsed.get("preco_final_50l"),
                    "preco_final_60l": parsed.get("preco_final_60l"),
                    "preco_atual_40l": parsed.get("preco_atual_40l"),
                    "preco_atual_50l": parsed.get("preco_atual_50l"),
                    "preco_atual_60l": parsed.get("preco_atual_60l"),
                }
        except Exception as e:
            _LOGGER.error("Erro ao buscar preços de %s: %s", self._fuel_type, e)
            self._state = None
            self._attributes = {}
