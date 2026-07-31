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
├── templates/              # Templates Jinja2 (blog e linktree)
│   ├── base.html           # Layout base: head, header, footer
│   ├── linktree.html       # Página de links (/linktree)
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
│   │   ├── blog.css        # Camada visual do blog (CRT, terminal, tipografia)
│   │   └── linktree.css    # Camada visual da página de links
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
| `GET` | `/linktree` | Página de links (estilo linktree, bilíngue in-place) |
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

## Idioma

Toda a lógica de idioma vive em `static/js/lang.js`, carregado de forma bloqueante no
`<head>` para resolver antes da primeira pintura. O idioma é resolvido nesta ordem:

1. escolha explícita salva em `localStorage` (`mdac:lang`);
2. idioma do navegador (`navigator.languages`);
3. inglês, como fallback.

Só a escolha explícita é persistida — a detecção continua dinâmica, para não congelar um
chute como se fosse decisão do usuário.

**Portfólio** (`/` e `/pt/`): páginas separadas por URL. Cada uma declara o próprio idioma
no `<html>` e o endereço da outra versão:

```html
<html lang="en" data-lang-page="en" data-lang-alt="/pt/">
```

Se o idioma resolvido não bate com o da página, o script faz `location.replace()` para a
alternativa. Como depois do redirecionamento o idioma passa a bater, não há loop.

**Blog** (`/blog`): uma única URL que traduz a interface no lugar. O `<html>` declara
`data-i18n-live`, e cada texto de interface recebe `data-i18n="chave"`:

```html
<a href="/#home" data-i18n="nav.home">Início</a>
<span data-i18n="blog.readingTime" data-i18n-n="{{ post.reading_time }}">3 min de leitura</span>
```

O HTML servido já vem em português, então quem está sem JavaScript continua lendo a página
inteira em português. `data-i18n-n` alimenta o `{n}` da tradução e escolhe entre `chave` e
`chave_one` no singular. Para adicionar um texto novo, inclua a chave nos **dois**
dicionários de `lang.js` — as tabelas `pt` e `en` devem ter exatamente as mesmas chaves.

Os posts são escritos só em português: o texto, os títulos e os resumos carregam
`lang="pt-br"` explícito, então continuam corretos para leitores de tela mesmo com a
interface em inglês. Com a interface em inglês, um aviso discreto informa que os posts
estão em português.

## Deploy

O projeto é hospedado na [Discloud](https://discloud.com). As configurações de deploy estão em `discloud.config`.

## Licença

Todos os direitos reservados. Uso pessoal e educativo.
