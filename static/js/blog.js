/* Efeito de digitação nos elementos [data-typewriter] */
(function () {
    const targets = document.querySelectorAll('[data-typewriter]');
    if (!targets.length) return;

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    targets.forEach((el) => {
        const text = el.dataset.typewriter;
        if (reduced) {
            el.textContent = text;
            return;
        }

        let i = 0;
        (function tick() {
            el.textContent = text.slice(0, i++);
            if (i <= text.length) setTimeout(tick, 45);
        })();
    });
})();

/* Filtro de posts por tag */
(function () {
    const buttons = document.querySelectorAll('.tag--btn');
    const items = document.querySelectorAll('.post-item');
    const empty = document.getElementById('no-results');
    if (!buttons.length || !items.length) return;

    buttons.forEach((button) => {
        button.addEventListener('click', () => {
            const tag = button.dataset.tag;

            buttons.forEach((other) => other.classList.toggle('is-active', other === button));

            let visible = 0;
            items.forEach((item) => {
                const tags = (item.dataset.tags || '').split(' ');
                const show = tag === '*' || tags.includes(tag);
                item.hidden = !show;
                if (show) visible++;
            });

            if (empty) empty.hidden = visible > 0;
        });
    });
})();
