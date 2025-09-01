import pytest
import re

def parse_variation(text: str):
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


def test_parse_variation_subida():
    text = "O preço do litro de gasóleo deverá subir até 0,5 cêntimos (0,005 euros/litro)"
    result = parse_variation(text)
    assert result["tendencia"] == "sobe"
    assert result["variacao"] == 0.5


def test_parse_variation_descida():
    text = "O preço do litro de gasolina deverá descer até -0,5 cêntimos (-0,005 euros/litro)"
    result = parse_variation(text)
    assert result["tendencia"] == "desce"
    assert result["variacao"] == -0.5


def test_parse_variation_neutro():
    text = "O preço do litro de gasolina deverá manter-se estável"
    result = parse_variation(text)
    assert result["tendencia"] == "neutro"
    assert result["variacao"] is None
