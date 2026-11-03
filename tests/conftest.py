import os

# Roda antes de qualquer teste: garante uma chave falsa para o import do analisador.
# Assim os testes funcionam até em máquinas sem .env, e nunca usam sua chave real.
os.environ.setdefault("GEMINI_API_KEY", "chave-falsa-para-testes")