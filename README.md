# Portfólio - Matheus de Alencar

Portfólio pessoal servido por uma API FastAPI, com suporte a dois idiomas (PT/EN), carregamento dinâmico de avaliações de projetos freelancer e um blog estático renderizado com Jinja2.

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
│   ├── request_site.py     # Scraper + cache de avaliações
│   └── blog.py             # Registro de posts (lê os metadados dos templates)
├── templates/              # Templates Jinja2 (blog)
│   ├── base.html           # Layout base: head, header, footer
│   └── blog/
│       ├── index.html      # Listagem de posts
│       ├── post.html       # Layout de um post
│       └── posts/          # Um arquivo por post — o nome vira a URL
├── static/
│   ├── index.html          # Portfólio em inglês
│   ├── pt/
│   │   └── index.html      # Portfólio em português
│   ├── css/
│   │   ├── main.css
│   │   └── blog.css        # Camada visual do blog (CRT, terminal, tipografia)
│   ├── js/
│   │   ├── main.js         # Menu, typewriter, glitch
│   │   ├── api.js          # Requisição e renderização dos feedbacks
│   │   ├── blog.js         # Efeito de digitação e filtro por tag
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
URL=https://site.com.br
PORT=1234
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
| `GET` | `/reviews` | Avaliações de clientes freelancer (cache de 24h) |
| `GET` | `/blog` | Listagem de posts |
| `GET` | `/blog/{slug}` | Post individual |
| `GET` | `/health` | Health check |
| `GET` | `/static/...` | Arquivos estáticos |

Documentação interativa disponível em `/docs` (Swagger UI).

## Escrevendo um post

Cada post é um template Jinja2 em `templates/blog/posts/`. **O nome do arquivo vira a
URL** (`primeiro-commit.html` → `/blog/primeiro-commit`) e os metadados moram no próprio
arquivo — não existe banco de dados nem índice para atualizar.

```jinja
{% extends "blog/post.html" %}

{% set post = {
    "title": "Primeiro commit",
    "date": "2026-07-29",
    "summary": "Uma frase que aparece na listagem.",
    "tags": ["python", "fastapi"],
} %}

{% block post_body %}
    <p>O texto do post, em HTML.</p>
{% endblock %}
```

- `title` e `date` (formato `AAAA-MM-DD`) são obrigatórios; `summary` e `tags` são opcionais.
- O tempo de leitura é calculado a partir do texto; para fixar, informe `reading_time`.
- Os posts são ordenados da data mais recente para a mais antiga. Para desempatar dois
  posts do mesmo dia, informe também a hora: `"date": "2026-07-29 21:30"`.
- Um post com metadados inválidos é ignorado na listagem, com um aviso no log — o blog não quebra.
- Se o texto contiver sintaxe Jinja (`{{ }}` ou `{% %}`), envolva o trecho em `{% raw %}`.

`templates/blog/posts/modelo-de-post.html` é uma referência viva de toda a marcação
disponível (títulos, listas, citações, notas, código, imagens e tabelas). Apague quando
não precisar mais.

## Deploy

O projeto é hospedado na [Discloud](https://discloud.com). As configurações de deploy estão em `discloud.config`.

## Licença

Todos os direitos reservados. Uso pessoal e educativo.
