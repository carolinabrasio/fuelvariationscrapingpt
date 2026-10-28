from custom_components.fuelvariationscrapingpt.sensor import extract_metric


def test_extract_metric_for_negative_forecast():
    html = """
        <time datetime="2026-04-24"></time>
        <h3>Gasóleo: sobe ou desce na próxima semana</h3>
        <p>A previsão aponta para uma descida de −0,04 €/l.</p>
        <section id="referencia">
            <p>Preço de referência 1,98 para gasóleo simples</p>
        </section>
        """

    result = extract_metric(html, "gasoleo")

    assert result == {
        "inicio_previsao": "2026-04-27",
        "fim_previsao": "2026-05-03",
        "atualizacao": "2026-04-24",
        "texto": "A previsão aponta para uma descida de −0,04 €/l.",
        "tendencia": "desce",
        "variacao": -4.0,
        "nivel_de_variacao": "moderada",
        "preco_referencia": 1.98,
        "preco_final": 1.94,
        "preco_final_40l": 77.6,
        "preco_final_50l": 97.0,
        "preco_final_60l": 116.4,
        "preco_atual_40l": 79.2,
        "preco_atual_50l": 99.0,
        "preco_atual_60l": 118.8,
        "impacto_40l": -1.6,
        "impacto_50l": -2.0,
        "impacto_60l": -2.4,
    }


def test_extract_metric_rejects_negative_decimal_reference_price():
    html = """
        <time datetime="2026-04-24"></time>
        <h3>Gasóleo: sobe ou desce na próxima semana</h3>
        <p>A previsão aponta para uma descida de −0,04 €/l.</p>
        <section id="referencia">
            <p>Preço de referência -1,00€/L para gasóleo simples</p>
        </section>
        """

    result = extract_metric(html, "gasoleo")

    assert result["preco_referencia"] is None
    assert result["preco_final"] is None
    assert result["impacto_40l"] == -1.6
    assert result["impacto_50l"] == -2.0
    assert result["impacto_60l"] == -2.4
    assert "preco_atual_40l" not in result

