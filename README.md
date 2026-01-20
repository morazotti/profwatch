# 🎓 ProfWatch

Monitoramento automatizado de concursos para docentes em universidades brasileiras (USP, UNICAMP, UNESP, UFSCar).

Este projeto utiliza **Python**, **FastAPI** e **Playwright** para realizar a raspagem de dados de portais universitários dinâmicos e apresenta os resultados em uma interface moderna e filtrável.

## 🚀 Como Rodar o Projeto

Para rodar este projeto diretamente do GitHub, siga os passos abaixo:

### 1. Pré-requisitos
Certifique-se de ter o [uv](https://github.com/astral-sh/uv) instalado. O `uv` é o gerenciador de pacotes e ambientes Python que utilizamos para maior velocidade e estabilidade.

```bash
# Instalar uv (se ainda não tiver)
curl -LsSf https://astral-sh.uv.io/install.sh | sh
```

### 2. Clonar e Instalar
Clone o repositório e instale as dependências:

```bash
git clone https://github.com/seu-usuario/profwatch.git
cd profwatch/backend
uv sync
```

### 3. Instalar os Navegadores do Playwright
O projeto utiliza o Playwright para navegar nos sites das universidades. Você precisa instalar os binários do navegador:

```bash
uv run playwright install chromium
```

### 4. Iniciar o Servidor
Com tudo instalado, inicie o servidor FastAPI:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Acessar a Interface
Abra o seu navegador em:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: FastAPI (Python)
- **Scraping**: Playwright (Automação de navegador)
- **Frontend**: HTML5, Vanilla CSS (Design Moderno/Dark Mode)
- **Gestão de Pacotes**: `uv`

## 📂 Estrutura do Projeto

- `backend/app/main.py`: Ponto de entrada da API e servidor de arquivos estáticos.
- `backend/app/scrapers/`: Contém a lógica de raspagem para cada universidade.
- `backend/app/static/`: Interface Web (HTML/CSS).
- `next-steps.md`: Roteiro de melhorias futuras.

---

## 📋 Observações
- Na primeira execução, o servidor realizará um "scraping inicial". Isso pode levar de 1 a 2 minutos dependendo da sua conexão.
- O cache em memória garante que as navegações subsequentes na interface sejam quase instantâneas.
