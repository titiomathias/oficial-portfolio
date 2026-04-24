# Portfólio - Matheus de Alencar

Portfólio pessoal servido por uma API FastAPI, com suporte a dois idiomas (PT/EN) e carregamento dinâmico de avaliações do 99freelas.

## Stack

- **Backend:** Python 3.12, FastAPI
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla + Axios + Glider.js)
- **Scraping:** cloudscraper + BeautifulSoup4
- **Deploy:** Discloud

## Estrutura

```
oficial-portfolio/
├── app.py                  # Aplicação FastAPI (rotas e servidor)
├── scripts/
│   └── request_site.py     # Scraper + cache de avaliações (99freelas)
├── static/
│   ├── index.html          # Portfólio em inglês
│   ├── pt/
│   │   └── index.html      # Portfólio em português
│   ├── css/main.css
│   ├── js/
│   │   ├── main.js         # Menu, typewriter, glitch
│   │   ├── api.js          # Requisição e renderização dos feedbacks
│   │   └── axios.min.js
│   ├── img/
│   └── files/              # CV para download
├── .env                    # Variáveis de ambiente (não versionado)
├── .env.example
├── requirements.txt
└── discloud.config
```

## Variáveis de ambiente

Crie um arquivo `.env` na raiz com base no `.env.example`:

```env
99URL=https://www.99freelas.com.br
```

## Instalação e execução local

```bash
# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar
fastapi dev app.py
```

A aplicação estará disponível em `http://localhost:8000`.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Portfólio em inglês |
| `GET` | `/pt` | Portfólio em português |
| `GET` | `/reviews` | Avaliações do 99freelas (cache de 24h) |
| `GET` | `/health` | Health check |
| `GET` | `/static/...` | Arquivos estáticos |

Documentação interativa disponível em `/docs` (Swagger UI).

## Deploy

O projeto é hospedado na [Discloud](https://discloud.com). As configurações de deploy estão em `discloud.config`.

## Licença

Todos os direitos reservados. Uso pessoal e educativo.
