import mimetypes
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

import json
from pydantic import ValidationError
from modelos import Prato

import time
from google.genai import errors

import os
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")  # carrega a chave do arquivo .env

CHAVE = os.getenv("GEMINI_API_KEY")
if not CHAVE:
    raise SystemExit(
        "GEMINI_API_KEY não encontrada. Confira se o arquivo .env está "
        "na mesma pasta do analisador.py e se o nome está correto."
    )

MODELO = [
    m for m in (os.getenv("MODELO", "gemini-3.8-flash"), os.getenv("MODELO_RESERVA")) if m
]  # confira o nome atual no AI Studio

client = genai.Client(api_key=CHAVE)  # usa GEMINI_API_KEY do ambiente

PROMPT = (
    "Analise o prato da imagem. Responda apenas em JSON com os campos: "
    "nome (string), ingredientes (lista de strings), "
    "culinaria (string), confianca (numero de 0 a 1)."
)


def chamar_modelo(modelo: str, imagem_bytes: bytes, mime: str):
    return client.models.generate_content(
        model=modelo,
        contents=[
            types.Part.from_bytes(data=imagem_bytes, mime_type=mime),
            PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )


def analisar_prato(imagem_bytes: bytes, mime: str, tentativas: int = 3) -> Prato:
    resposta = None
    ultimo_erro = None

    for modelo in MODELO:
        for i in range(tentativas):
            try:
                resposta = chamar_modelo(modelo, imagem_bytes, mime)
                break
            except errors.APIError as erro:
                if erro.code not in (429, 503):
                    raise  # erro permanente: tentar de novo não adianta
                ultimo_erro = erro
                if i < tentativas - 1:
                    espera = 2 ** (i + 1)
                    print(f"[{modelo}] erro {erro.code}. Nova tentativa em {espera}s...")
                    time.sleep(espera)
        if resposta is not None:
            break
        print(f"Modelo {modelo} indisponível. Passando para o próximo...")

    if resposta is None:
        raise ultimo_erro

    try:
        dados = json.loads(resposta.text)
        return Prato(**dados)
    except (json.JSONDecodeError, ValidationError, TypeError) as erro:
        raise ValueError(f"Resposta inválida do modelo: {erro}")


if __name__ == "__main__":
    caminho = sys.argv[1]
    mime, _ = mimetypes.guess_type(caminho)
    with open(caminho, "rb") as f:
        imagem = f.read()

    try:
        prato = analisar_prato(imagem, mime)
        print(prato.model_dump_json(indent=2))
    except errors.APIError as erro:
        raise SystemExit(f"Serviço de IA indisponível no momento (erro {erro.code}). Tente de novo em alguns minutos.")
    except ValueError as erro:
        raise SystemExit(str(erro))