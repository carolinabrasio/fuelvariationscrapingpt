import sys
import os
import pytest

# garante que a raiz do projeto está no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from custom_components.fuelvariationscraping import parser


def test_parse_variation_subida():
    text = "O preço do litro de gasóleo deverá subir até 0,5 cêntimos (0,005 euros/litro)"
    result = parser.parse_variation(text)
    assert result["tendencia"] == "sobe"
    assert result["variacao"] == 0.5


def test_parse_variation_descida():
    text = "O preço do litro de gasolina deverá descer até -0,5 cêntimos (-0,005 euros/litro)"
    result = parser.parse_variation(text)
    assert result["tendencia"] == "desce"
    assert result["variacao"] == -0.5


def test_parse_variation_neutro():
    text = "O preço do litro de gasolina deverá manter-se estável"
    result = parser.parse_variation(text)
    assert result["tendencia"] == "neutro"
    assert result["variacao"] is None
