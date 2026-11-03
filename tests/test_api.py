import pytest
from fastapi.testclient import TestClient
from google.genai import errors

import main
from modelos import Prato

client = TestClient(main.app)

IMAGEM_FALSA = b"bytes-de-imagem-falsa"


@pytest.fixture(autouse=True)
def bloquear_modelo_real(monkeypatch):
    """Por padrão, qualquer teste que tente chamar o modelo falha."""

    def proibido(*args, **kwargs):
        raise AssertionError("O teste tentou chamar o modelo real!")

    monkeypatch.setattr(main, "analisar_prato", proibido)


def enviar(conteudo=IMAGEM_FALSA, nome="foto.jpg", tipo="image/jpeg"):
    return client.post("/analisar", files={"arquivo": (nome, conteudo, tipo)})


def prato_valido():
    return Prato(
        e_prato=True,
        nome="Pizza Margherita",
        ingredientes=["massa", "queijo", "tomate"],
        culinaria="Italiana",
        confianca=0.95,
    )


def test_saude():
    resposta = client.get("/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_prato_valido_retorna_200(monkeypatch):
    monkeypatch.setattr(main, "analisar_prato", lambda conteudo, tipo: prato_valido())

    resposta = enviar()

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Pizza Margherita"
    assert resposta.json()["e_prato"] is True


def test_imagem_que_nao_e_prato_retorna_422(monkeypatch):
    nao_prato = Prato(e_prato=False, confianca=0.9)
    monkeypatch.setattr(main, "analisar_prato", lambda conteudo, tipo: nao_prato)

    resposta = enviar()

    assert resposta.status_code == 422
    assert "não parece conter um prato" in resposta.json()["detail"]


def test_formato_invalido_retorna_415():
    resposta = enviar(conteudo=b"texto", nome="nota.txt", tipo="text/plain")
    assert resposta.status_code == 415


def test_arquivo_vazio_retorna_400():
    resposta = enviar(conteudo=b"")
    assert resposta.status_code == 400


def test_imagem_grande_demais_retorna_413():
    cinco_mb_e_um = b"0" * (5 * 1024 * 1024 + 1)
    resposta = enviar(conteudo=cinco_mb_e_um)
    assert resposta.status_code == 413


def test_servico_de_ia_indisponivel_retorna_503(monkeypatch):
    def falha(conteudo, tipo):
        raise errors.ServerError(503, {"error": {"message": "sobrecarga"}})

    monkeypatch.setattr(main, "analisar_prato", falha)

    resposta = enviar()

    assert resposta.status_code == 503
    assert "indisponível" in resposta.json()["detail"]


def test_resposta_invalida_do_modelo_retorna_502(monkeypatch):
    def falha(conteudo, tipo):
        raise ValueError("Resposta inválida do modelo")

    monkeypatch.setattr(main, "analisar_prato", falha)

    resposta = enviar()

    assert resposta.status_code == 502