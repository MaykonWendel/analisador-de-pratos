# 🍽️ Analisador de Pratos

API que recebe a foto de um prato e devolve, em JSON estruturado, o nome, os ingredientes prováveis, a culinária e o nível de confiança, usando o Gemini (LLM multimodal).

## O que o projeto demonstra

- Integração com um LLM via API, com saída em JSON.
- Validação da resposta do modelo com Pydantic, sem confiar no formato que ele devolve.
- Tratamento de falhas: retry com espera crescente e troca para um modelo reserva (fallback).
- Recusa de imagens que não são comida, com o código HTTP adequado.
- Testes automatizados com mocks, sem chamar o serviço real.

## Como funciona

1. A API recebe a imagem em `POST /analisar`.
2. Valida formato (JPEG, PNG ou WEBP), tamanho (até 5 MB) e se o arquivo não está vazio.
3. Envia a imagem ao modelo principal. Se ele estiver sobrecarregado (erro 429 ou 503), tenta de novo com espera crescente e, se continuar falhando, passa para o modelo reserva.
4. Valida a resposta com Pydantic. Se a imagem não for um prato, responde com erro 422.

## Exemplo

Requisição:

```bash
curl -X POST http://localhost:8000/analisar -F "arquivo=@prato.jpg;type=image/jpeg"
```

Resposta (200):

```json
{
  "e_prato": true,
  "nome": "[nome retornado]",
  "ingredientes": ["[...]"],
  "culinaria": "[...]",
  "confianca": 0.0
}
```

Códigos de erro:

| Código | Quando acontece |
|--------|-----------------|
| 400 | Arquivo vazio |
| 413 | Imagem maior que 5 MB |
| 415 | Formato não suportado |
| 422 | A imagem não parece conter um prato |
| 502 | O modelo devolveu uma resposta inválida |
| 503 | Serviço de IA indisponível, mesmo após retry e fallback |

## Como rodar

Pré-requisitos: Python 3.10+ e uma chave de API do Gemini (Google AI Studio).

```powershell
git clone https://github.com/MaykonWendel/analisador-de-pratos.git
cd analisador-de-pratos
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edite o `.env` e coloque a sua chave em `GEMINI_API_KEY`. Depois:

```powershell
uvicorn main:app --reload
```

Abra http://localhost:8000/docs para testar pelo navegador.

## Testes

```powershell
pytest -v
```

Os testes usam mocks no lugar do Gemini. Eles cobrem resposta válida, JSON quebrado, campos faltando, retry em 503, fallback para o modelo reserva, erro permanente (sem retry) e os erros da API.

## Decisões técnicas

- **Validação com Pydantic:** a resposta de um LLM não tem garantia de formato, então ela é validada antes de ser devolvida.
- **Retry só em erros temporários:** 429 e 503 são repetidos. Erros como chave inválida ou modelo inexistente falham na hora, porque tentar de novo não resolve.
- **Fallback de modelo:** na prática, o modelo principal retornou 503 por alta demanda durante o desenvolvimento, e o modelo reserva assumiu e respondeu.
- **Campo `e_prato`:** em vez de depender de um limite de confiança, o modelo informa explicitamente se a imagem é um prato. Antes disso, uma foto de cadeira voltava como "prato" com confiança 0 e status 200.
- **Modelos configuráveis por `.env`:** os nomes de modelo mudam com frequência, então ficam fora do código.

## Limitações

- [Escreva o que você observou nos testes. Exemplo: como o modelo se comportou com bebidas, sobremesas ou fotos com vários pratos.]
- Os ingredientes são estimados a partir da imagem e podem estar errados.
- Não há autenticação nem limite de requisições por usuário.

## Próximos passos

- Documentar o erro 422 de "não é prato" no Swagger.
- Adicionar autenticação e limite de requisições.
- Empacotar com Docker.