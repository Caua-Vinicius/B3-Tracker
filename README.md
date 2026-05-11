# 💎 B3 Tracker Premium Dashboard

Um Dashboard Financeiro minimalista e premium para acompanhamento em tempo real de ativos de Renda Variável (Ações e FIIs da B3). Construído com **Python**, **Streamlit**, **Plotly** e **SQLite**.

---

## 🚀 Como Executar o Projeto

Você pode rodar este projeto de duas formas: **Localmente** ou via **Docker**. Escolha a que preferir!

### Opção 1: Rodando Localmente (Recomendado para desenvolvimento)

1. **Abra o terminal na pasta do projeto.**
2. **Crie e ative um ambiente virtual (Opcional, mas recomendado):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Instale as dependências:**
   ```powershell
   pip install -r requirements.txt
   ```
4. **Execute a aplicação:**
   ```powershell
   streamlit run app.py
   ```
5. **Acesse no navegador:** A aplicação será aberta automaticamente, ou você pode acessar `http://localhost:8501`.

> 💡 **Nota sobre os Dados:** O banco de dados (`portfolio.db`) será criado automaticamente dentro da pasta `data/` na raiz do seu projeto local.

---

### Opção 2: Rodando via Docker (Recomendado para uso rápido)

Você não precisa instalar o Python ou dependências na sua máquina, basta ter o **Docker Desktop** (ou Docker/Docker Compose) instalado.

1. **Abra o terminal na pasta do projeto.**
2. **Construa e inicie o container:**
   ```powershell
   docker-compose up -d --build
   ```
3. **Acesse no navegador:** `http://localhost:8501`.

**Comandos Úteis do Docker:**
* Para ver se está tudo funcionando (logs): `docker logs -f b3-tracker-app`
* Para parar a aplicação: `docker-compose down`

> 💡 **Nota sobre os Dados:** O banco de dados fica salvo dentro de um volume isolado do Docker. Se você desejar que a versão Docker compartilhe exatamente a mesma pasta `data/` do seu computador local (para ter os mesmos ativos das duas formas), abra o arquivo `docker-compose.yml` e altere a linha `- b3_data:/app/data` para `- ./data:/app/data`.

---

## 🛠️ Stack Tecnológica
* **Frontend:** Streamlit
* **Gráficos:** Plotly Express (Interativos)
* **Banco de Dados:** SQLite + SQLAlchemy (ORM)
* **Dados de Mercado:** Biblioteca yfinance (otimizada com cache para evitar bloqueios de API)
