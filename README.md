# Portfólio - Matheus de Alencar

Portfólio pessoal servido por uma API FastAPI, com suporte a dois idiomas (PT/EN), carregamento dinâmico de avaliações de projetos freelancer e uma página de links renderizada com Jinja2.

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
│   └── sitemap.py          # Geração do sitemap.xml
├── templates/              # Templates Jinja2
│   ├── base.html           # Layout base: head, header, footer
│   └── linktree.html       # Página de links (/linktree)
├── static/
│   ├── index.html          # Portfólio em inglês
│   ├── pt/
│   │   └── index.html      # Portfólio em português
│   ├── css/
│   │   ├── main.css
│   │   ├── shell.css       # Casca das páginas Jinja2 (CRT, terminal, layout)
│   │   └── linktree.css    # Camada visual da página de links
│   ├── js/
│   │   ├── main.js         # Menu, typewriter, glitch
│   │   ├── api.js          # Requisição e renderização dos feedbacks
│   │   ├── typewriter.js   # Efeito de digitação
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
FEEDBACKS_MIRROR=https://raw.githubusercontent.com/titiomathias/oficial-portfolio/main/scripts/feedbacks.json
```

`FEEDBACKS_MIRROR` é opcional e serve à produção: veja [Avaliações](#avaliações).

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
| `GET` | `/linktree` | Página de links (estilo linktree, bilíngue in-place) |
| `GET` | `/health` | Health check |
| `GET` | `/static/...` | Arquivos estáticos |

Documentação interativa disponível em `/docs` (Swagger UI).

## Avaliações

O Cloudflare do 99freelas devolve **403 para IPs de datacenter**, então a VPS não
consegue raspar o perfil — nenhum ajuste de header resolve isso, é bloqueio por
reputação de IP. A coleta acontece fora dela:

1. O workflow `.github/workflows/feedbacks.yml` roda `python -m scripts.request_site`
   (semanalmente ou sob demanda) e commita `scripts/feedbacks.json` quando muda.
   Precisa da variável de repositório `URL` em *Settings → Secrets and variables →
   Actions → Variables*.
2. Em produção, `FEEDBACKS_MIRROR` aponta para esse JSON no GitHub. A VPS tenta o
   site, cai no espelho e, se os dois falharem, serve o cache em disco —
   `/reviews` nunca responde 500 por causa do bloqueio.
3. Se a CI também for bloqueada, rode `python -m scripts.request_site` na máquina
   local e commite o JSON. O espelho continua funcionando igual.

O cache em disco vale 24h; depois de uma falha, novas tentativas ficam seguras por
1h para não bater no Cloudflare a cada acesso.

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

**Linktree** (`/linktree`): uma única URL que traduz a interface no lugar. O `<html>`
declara `data-i18n-live`, e cada texto de interface recebe `data-i18n="chave"`:

```html
<a href="/#home" data-i18n="nav.home">Início</a>
<span class="lt-link__title" data-i18n="linktree.cv">Currículo</span>
```

O HTML servido já vem em português, então quem está sem JavaScript continua lendo a página
inteira em português. `data-i18n-n` alimenta o `{n}` da tradução e escolhe entre `chave` e
`chave_one` no singular. Para adicionar um texto novo, inclua a chave nos **dois**
dicionários de `lang.js` — as tabelas `pt` e `en` devem ter exatamente as mesmas chaves.

## Deploy

O projeto é hospedado na [Discloud](https://discloud.com). As configurações de deploy estão em `discloud.config`.

## Licença

Todos os direitos reservados. Uso pessoal e educativo.
