import json
from types import SimpleNamespace

import pytest
from google.genai import errors

import analisador
from modelos import Prato

JSON_VALIDO = json.dumps(
    {
        "e_prato": True,
        "nome": "Pizza Margherita",
        "ingredientes": ["massa", "queijo"],
        "culinaria": "Italiana",
        "confianca": 0.95,
    }
)


def resposta_com(texto):
    return SimpleNamespace(text=texto)


def erro_503():
    return errors.ServerError(503, {"error": {"message": "sobrecarga"}})


@pytest.fixture(autouse=True)
def sem_espera(monkeypatch):
    """Os testes nÃ£o precisam esperar 2s e 4s de verdade entre as tentativas."""
    monkeypatch.setattr(analisador.time, "sleep", lambda segundos: None)


def test_resposta_valida_vira_prato(monkeypatch):
    monkeypatch.setattr(
        analisador, "chamar_modelo", lambda modelo, imagem, mime: resposta_com(JSON_VALIDO)
    )

    prato = analisador.analisar_prato(b"x", "image/jpeg")

    assert isinstance(prato, Prato)
    assert prato.nome == "Pizza Margherita"


@pytest.mark.parametrize(
    "texto",
    [
        "isso nao e json",
        json.dumps({"nome": "faltam campos"}),
        json.dumps({"e_prato": True, "confianca": 5}),
    ],
    ids=["nao-e-json", "campos-faltando", "confianca-fora-do-intervalo"],
)
def test_resposta_invalida_levanta_valueerror(monkeypatch, texto):
    monkeypatch.setattr(
        analisador, "chamar_modelo", lambda modelo, imagem, mime: resposta_com(texto)
    )

    with pytest.raises(ValueError):
        analisador.analisar_prato(b"x", "image/jpeg")


def test_tenta_de_novo_quando_da_503(monkeypatch):
    chamadas = []

    def chamar(modelo, imagem, mime):
        chamadas.append(modelo)
        if len(chamadas) == 1:
            raise erro_503()
        return resposta_com(JSON_VALIDO)

    monkeypatch.setattr(analisador, "chamar_modelo", chamar)
    monkeypatch.setattr(analisador, "MODELO", ["principal"])

    prato = analisador.analisar_prato(b"x", "image/jpeg")

    assert prato.nome == "Pizza Margherita"
    assert len(chamadas) == 2


def test_usa_modelo_reserva_quando_principal_falha(monkeypatch):
    chamadas = []

    def chamar(modelo, imagem, mime):
        chamadas.append(modelo)
        if modelo == "principal":
            raise erro_503()
        return resposta_com(JSON_VALIDO)

    monkeypatch.setattr(analisador, "chamar_modelo", chamar)
    monkeypatch.setattr(analisador, "MODELO", ["principal", "reserva"])

    prato = analisador.analisar_prato(b"x", "image/jpeg")

    assert prato.nome == "Pizza Margherita"
    assert chamadas == ["principal", "principal", "principal", "reserva"]


def test_falha_em_todos_os_modelos_levanta_erro(monkeypatch):
    chamadas = []

    def chamar(modelo, imagem, mime):
        chamadas.append(modelo)
        raise erro_503()

    monkeypatch.setattr(analisador, "chamar_modelo", chamar)
    monkeypatch.setattr(analisador, "MODELO", ["principal", "reserva"])

    with pytest.raises(errors.APIError):
        analisador.analisar_prato(b"x", "image/jpeg")

    assert chamadas == ["principal"] * 3 + ["reserva"] * 3


def test_erro_permanente_nao_tenta_de_novo(monkeypatch):
    chamadas = []

    def chamar(modelo, imagem, mime):
        chamadas.append(modelo)
        raise errors.ClientError(404, {"error": {"message": "modelo nÃ£o existe"}})

    monkeypatch.setattr(analisador, "chamar_modelo", chamar)
    monkeypatch.setattr(analisador, "MODELO", ["principal", "reserva"])

    with pytest.raises(errors.ClientError):
        analisador.analisar_prato(b"x", "image/jpeg")

    assert len(chamadas) == 1
