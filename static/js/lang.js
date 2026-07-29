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
            'blog.langNotice': 'Os posts são escritos em português.'
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
            'blog.langNotice': 'Posts are written in Portuguese.'
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

    function resolve() {
        return stored() || fromBrowser();
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

    var pageLang = normalize(html.getAttribute('data-lang-page'));
    var alt = html.getAttribute('data-lang-alt');
    var lang = resolve();

    if (pageLang && alt && lang !== pageLang) {
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
