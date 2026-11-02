# 🍽️ Analisador de Pratos com Gemini

API que analisa fotos de pratos usando o Gemini e devolve dados estruturados em formato JSON (nome do prato, ingredientes, tipo de culinária e nível de confiança).

---

## 🚀 Tecnologias Utilizadas

* **Python 3.x**
* **Google GenAI SDK** (`google-genai`)
* **python-dotenv** (gerenciamento de variáveis de ambiente)

---

## ⚙️ Pré-requisitos e Instalação

1. Clone o repositório:
   ```bash
   git clone [https://github.com/MaykonWendel/analisador-de-pratos.git](https://github.com/MaykonWendel/analisador-de-pratos.git)
   cd analisador-de-pratos

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt

3. Crie um arquivo .env na raiz do projeto e adicione sua chave de API do Gemini:
   ```bash
   GEMINI_API_KEY=sua_chave_aqui
   MODELO=gemini-2.5-flash


## 💡Como usar

1. Execute o script (`analisador.py`) passando o caminho da imagem como argumento:
   ```bash
   python analisador.py caminho/para/imagem.jpg

  Exemplo de resposta(JSon)
  ```bash
      {
        "nome": "Feijoada",
        "ingredientes": ["Feijão preto", "Carne seca", "Linguiça", "Arroz", "Couve", "Farofa"],
        "culinaria": "Brasileira",
        "confianca": 0.98
      }
  ```

## 👨‍💻 Autor
Desenvolvido por @MaykonWendel.

   
