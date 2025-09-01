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
