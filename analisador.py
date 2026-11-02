import mimetypes
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

import os
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")  # carrega a chave do arquivo .env

CHAVE = os.getenv("GEMINI_API_KEY")
if not CHAVE:
    raise SystemExit(
        "GEMINI_API_KEY não encontrada. Confira se o arquivo .env está "
        "na mesma pasta do analisador.py e se o nome está correto."
    )

MODELO = os.getenv("MODELO", "gemini-3.8-flash")  # confira o nome atual no AI Studio

client = genai.Client(api_key=CHAVE)  # usa GEMINI_API_KEY do ambiente

PROMPT = (
    "Analise o prato da imagem. Responda apenas em JSON com os campos: "
    "nome (string), ingredientes (lista de strings), "
    "culinaria (string), confianca (numero de 0 a 1)."
)


def analisar_prato(imagem_bytes: bytes, mime: str) -> str:
    resposta = client.models.generate_content(
        model=MODELO,
        contents=[
            types.Part.from_bytes(data=imagem_bytes, mime_type=mime),
            PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )
    return resposta.text


if __name__ == "__main__":
    import time

    caminho = sys.argv[1]
    mime, _ = mimetypes.guess_type(caminho)
    with open(caminho, "rb") as f:
        imagem = f.read()

    print("Enviando para o modelo...")
    inicio = time.time()
    print(analisar_prato(imagem, mime))
    print(f"\nTempo: {time.time() - inicio:.1f}s")