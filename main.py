from fastapi import FastAPI, File, HTTPException, UploadFile
from google.genai import errors

from analisador import analisar_prato
from modelos import Prato

app = FastAPI(title="Analisador de Pratos")

TIPOS_ACEITOS = {"image/jpeg", "image/png", "image/webp"}
TAMANHO_MAXIMO = 5 * 1024 * 1024  # 5 MB


@app.get("/saude")
def saude():
    return {"status": "ok"}


@app.post("/analisar", response_model=Prato)
def analisar(arquivo: UploadFile = File(...)):
    if arquivo.content_type not in TIPOS_ACEITOS:
        raise HTTPException(
            status_code=415,
            detail="Formato não suportado. Envie JPEG, PNG ou WEBP.",
        )

    conteudo = arquivo.file.read(TAMANHO_MAXIMO + 1)
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(status_code=413, detail="Imagem maior que 5 MB.")
    if not conteudo:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    try:
        prato = analisar_prato(conteudo, arquivo.content_type)
    except errors.APIError:
        raise HTTPException(
            status_code=503,
            detail="Serviço de IA indisponível no momento. Tente novamente em alguns minutos.",
        )
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="O modelo devolveu uma resposta inválida. Tente novamente.",
        )

    if not prato.e_prato:
        raise HTTPException(
            status_code=422,
            detail="A imagem não parece conter um prato de comida.",
        )
    return prato