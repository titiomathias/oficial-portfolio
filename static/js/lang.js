(function () {
    'use strict';

    var STORAGE_KEY = 'mdac:lang';
    var SUPPORTED = ['pt', 'en'];
    var FALLBACK = 'en';

    var DICT = {
        pt: {
            'nav.home': 'Início',
            'nav.services': 'Serviços',
            'nav.portfolio': 'Portfólio',
            'nav.contact': 'Contato',
            'nav.blog': 'Blog',
            'nav.language': 'Idioma',
            'nav.english': 'Inglês',
            'nav.portuguese': 'Português',
            'footer.rights': 'Copyright © 2026 por Matheus de Alencar. Todos os direitos reservados.',
            'blog.records': '{n} registros encontrados.',
            'blog.records_one': '{n} registro encontrado.',
            'blog.intro': 'Anotações sobre projetos pessoais, estudos e a jornada de virar uma pessoa melhor. Sem pauta, sem calendário editorial. Apenas o que valeu a pena escrever.',
            'blog.filter': '// filtrar:',
            'blog.all': 'todos',
            'blog.readingTime': '{n} min de leitura',
            'blog.noResults': 'nenhum post com essa tag.',
            'blog.empty': 'nenhum post publicado ainda. volte em breve.',
            'post.eof': 'EOF — obrigado por ler até aqui.',
            'post.prev': '<< anterior',
            'post.next': 'próximo >>',
            'blog.langNotice': 'Os posts são escritos em português.',
            'linktree.role': 'Dev Full-Stack · Hacker Ético · Software Engineer',
            'linktree.intro': 'Engenharia de software e segurança ofensiva. Aqui ficam todos os canais: onde eu escrevo, onde eu publico código e onde me chamar para um projeto.',
            'linktree.group.content': '// conteúdo',
            'linktree.group.contact': '// contato',
            'linktree.group.social': '// redes',
            'linktree.group.highlights': '// destaques',
            'linktree.portfolio': 'Portfólio',
            'linktree.portfolio.desc': 'Projetos, serviços, prêmios e a trajetória completa.',
            'linktree.blog': 'Blog',
            'linktree.blog.desc': 'Notas sobre projetos pessoais, estudos e segurança.',
            'linktree.cv': 'Currículo',
            'linktree.cv.desc': 'PDF atualizado, pronto para download.',
            'linktree.whatsapp.desc': 'Resposta mais rápida. Dúvidas e orçamentos.',
            'linktree.email': 'E-mail',
            'linktree.email.desc': 'Propostas formais, NDAs e escopos de pentest.',
            'linktree.linkedin.desc': 'Rede profissional, vagas e parcerias.',
            'linktree.github.desc': 'Código aberto, scripts e experimentos.',
            'linktree.instagram.desc': 'Bastidores, eventos e o lado menos técnico.',
            'linktree.tedx.desc': 'Palestrante convidado do evento.',
            'linktree.ctf': 'Top 1 — CTF BSides SP 2026',
            'linktree.ctf.desc': '1º lugar com o time Duckware.',
            'linktree.mai.desc': 'Startup incubada no Inatel — análise de empresas.',
            'linktree.back': 'cd .. # voltar ao portfólio'
        },
        en: {
            'nav.home': 'Home',
            'nav.services': 'Services',
            'nav.portfolio': 'Portfolio',
            'nav.contact': 'Contact',
            'nav.blog': 'Blog',
            'nav.language': 'Language',
            'nav.english': 'English',
            'nav.portuguese': 'Portuguese',
            'footer.rights': 'Copyright © 2026 by Matheus de Alencar. All Rights Reserved.',
            'blog.records': '{n} entries found.',
            'blog.records_one': '{n} entry found.',
            'blog.intro': 'Notes on personal projects, studies and the journey of becoming a better person. No editorial calendar, no agenda. Just what was worth writing down.',
            'blog.filter': '// filter:',
            'blog.all': 'all',
            'blog.readingTime': '{n} min read',
            'blog.noResults': 'no posts with that tag.',
            'blog.empty': 'nothing published yet. check back soon.',
            'post.eof': 'EOF — thanks for reading this far.',
            'post.prev': '<< previous',
            'post.next': 'next >>',
            'blog.langNotice': 'Posts are written in Portuguese.',
            'linktree.role': 'Full-Stack Dev · Ethical Hacker · Software Engineer',
            'linktree.intro': 'Software engineering and offensive security. Every channel in one place: where I write, where I ship code and where to reach me for a project.',
            'linktree.group.content': '// content',
            'linktree.group.contact': '// contact',
            'linktree.group.social': '// social',
            'linktree.group.highlights': '// highlights',
            'linktree.portfolio': 'Portfolio',
            'linktree.portfolio.desc': 'Projects, services, awards and the full track record.',
            'linktree.blog': 'Blog',
            'linktree.blog.desc': 'Notes on personal projects, studies and security.',
            'linktree.cv': 'Résumé',
            'linktree.cv.desc': 'Up-to-date PDF, ready to download.',
            'linktree.whatsapp.desc': 'Fastest response. Questions and quotes.',
            'linktree.email': 'Email',
            'linktree.email.desc': 'Formal proposals, NDAs and pentest scopes.',
            'linktree.linkedin.desc': 'Professional network, roles and partnerships.',
            'linktree.github.desc': 'Open source, scripts and experiments.',
            'linktree.instagram.desc': 'Behind the scenes, events and the less technical side.',
            'linktree.tedx.desc': 'Invited speaker at the event.',
            'linktree.ctf': 'Top 1 — CTF BSides SP 2026',
            'linktree.ctf.desc': '1st place with team Duckware.',
            'linktree.mai.desc': 'Startup incubated at Inatel — company analysis.',
            'linktree.back': 'cd .. # back to the portfolio'
        }
    };

    var html = document.documentElement;

    function normalize(tag) {
        if (!tag) return null;
        var base = String(tag).toLowerCase().split('-')[0];
        return SUPPORTED.indexOf(base) !== -1 ? base : null;
    }

    /* localStorage pode lançar em modo privado ou com cookies bloqueados. */
    function stored() {
        try {
            return normalize(window.localStorage.getItem(STORAGE_KEY));
        } catch (e) {
            return null;
        }
    }

    function save(lang) {
        try {
            window.localStorage.setItem(STORAGE_KEY, lang);
        } catch (e) {
            /* preferência não persiste, mas a troca da sessão atual funciona */
        }
    }

    function fromBrowser() {
        var tags = (navigator.languages && navigator.languages.length)
            ? navigator.languages
            : [navigator.language];

        for (var i = 0; i < tags.length; i++) {
            var lang = normalize(tags[i]);
            if (lang) return lang;
        }
        return FALLBACK;
    }

    function translate(lang, key, count) {
        var table = DICT[lang] || DICT[FALLBACK];
        var value = (count === 1 && table[key + '_one']) ? table[key + '_one'] : table[key];
        if (value === undefined) return null;
        return count === null ? value : value.replace('{n}', count);
    }

    function apply(lang) {
        html.lang = (lang === 'pt') ? 'pt-br' : 'en';
        html.setAttribute('data-lang', lang);

        var nodes = document.querySelectorAll('[data-i18n]');
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i];
            var raw = node.getAttribute('data-i18n-n');
            var count = (raw === null) ? null : Number(raw);
            var text = translate(lang, node.getAttribute('data-i18n'), count);
            if (text !== null) node.textContent = text;
        }
    }

    /* --- 1. Redirecionamento nas páginas do portfólio ---------------------- */

    /* Dois sinais, duas regras diferentes de propósito:

       - Escolha explícita (localStorage): redireciona em qualquer direção. É uma
         preferência que o visitante declarou clicando no seletor de idioma.

       - Idioma do navegador (inferido): só redireciona a partir da página de
         entrada, marcada com data-lang-entry — que é a mesma anunciada como
         x-default no hreflang.

       Antes o idioma do navegador valia em qualquer página, e isso expulsava o
       Googlebot de /pt/: ele renderiza com navigator.language = "en-US", então
       era mandado para / antes de indexar, e a versão em português nunca entrava
       no índice. Bots não têm localStorage, logo nunca caem na primeira regra. */

    var pageLang = normalize(html.getAttribute('data-lang-page'));
    var alt = html.getAttribute('data-lang-alt');
    var choice = stored();
    var lang = choice || fromBrowser();
    var isEntryPage = html.hasAttribute('data-lang-entry');

    if (pageLang && alt && lang !== pageLang && (choice || isEntryPage)) {
        /* replace() em vez de assign(): o botão voltar não fica preso no loop. */
        window.location.replace(alt);
        return;
    }

    /* --- 2. Tradução da interface e troca de idioma ------------------------ */

    function wire() {
        var live = html.hasAttribute('data-i18n-live');

        if (live) apply(lang);

        var links = document.querySelectorAll('[data-lang-choice]');
        for (var i = 0; i < links.length; i++) {
            links[i].addEventListener('click', function (event) {
                var choice = normalize(this.getAttribute('data-lang-choice'));
                if (!choice) return;

                save(choice);

                /* No blog dá para trocar sem sair da página; no portfólio o
                   href leva para a versão traduzida e a navegação segue. */
                if (live) {
                    event.preventDefault();
                    lang = choice;
                    apply(choice);
                }
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', wire);
    } else {
        wire();
    }
})();
