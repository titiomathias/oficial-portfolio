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
