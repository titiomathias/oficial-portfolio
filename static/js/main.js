/* Animation hamburguer */

function toggleMenu() {
    const nav = document.querySelector('.nav-responsive');
    menuHamburguer.classList.toggle('change');

    if (menuHamburguer.classList.contains('change')) {
        nav.style.display = 'block';
    } else {
        nav.style.display = 'none';
    }
}

const menuHamburguer = document.querySelector('.menu-hamburguer');

menuHamburguer.addEventListener('click', () => {
    toggleMenu();
});

/* Read More Event */
document.addEventListener("DOMContentLoaded", () => {
    const readMoreButtons = document.querySelectorAll(".services-box .btn");

    const dropdowns = document.querySelectorAll(".nav-responsive .dropdown");

    dropdowns.forEach(dropdown => {
        dropdown.addEventListener("click", () => {

            const languages = dropdown.querySelector(".language");

            if (languages.style.display === "block") {
                languages.style.display = "none";
            } else {
                languages.style.display = "block";
            }
        });
    });

    readMoreButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            const servicesBox = button.closest(".services-box");
            const paragraph = servicesBox.querySelector("p");

            const isExpanded = paragraph.getAttribute("data-expanded") === "true";

            if (isExpanded) {
                paragraph.style.display = "-webkit-box";
                paragraph.style.overflow = "hidden";
                paragraph.style.textOverflow = "ellipsis";
                paragraph.setAttribute("data-expanded", "false");

                if (button.textContent === "Read less") {
                    button.textContent = "Read more";
                } else {
                    button.textContent = "Saiba mais";
                }
            } else {
                paragraph.style.display = "block";
                paragraph.style.overflow = "visible";
                paragraph.style.textOverflow = "unset";
                paragraph.setAttribute("data-expanded", "true");

                if (button.textContent === "Read more") {
                    button.textContent = "Read less";
                } else {
                    button.textContent = "Saiba menos";
                }
            }
        });
    });
});

/* Scroll — header compact */
window.addEventListener('scroll', () => {
    document.querySelector('header').classList.toggle('header--scrolled', window.scrollY > 60);
});

/* Typewriter role switcher */
(function () {
    const el = document.getElementById('role-text');
    if (!el) return;
    const lang = document.documentElement.lang;
    const roles = lang === 'pt'
        ? ['Desenvolvedor Full-Stack', 'Hacker Ético', 'Pentester', 'Engenheiro de Software']
        : ['Full-Stack Developer', 'Ethical Hacker', 'Pentester', 'Software Engineer'];
    let ri = 0, ci = 0, deleting = false;
    function tick() {
        const word = roles[ri];
        el.textContent = deleting ? word.slice(0, ci--) : word.slice(0, ci++);
        if (!deleting && ci > word.length)  { deleting = true; setTimeout(tick, 1800); return; }
        if (deleting && ci < 0)             { deleting = false; ri = (ri + 1) % roles.length; ci = 0; }
        setTimeout(tick, deleting ? 40 : 80);
    }
    tick();
})();

/* Name glitch — cycles through aliases on the h1 */
(function () {
    const h1 = document.querySelector('.home-content h1');
    if (!h1) return;
    const original = 'Matheus';
    const aliases = ['Mathias', 'Alencar', 'AltDel', 'Matheus', "Matt", "Math"];

    function triggerGlitch() {
        const alias = aliases[Math.floor(Math.random() * aliases.length)];
        h1.textContent = alias;
        h1.classList.add('glitching');

        setTimeout(() => {
            h1.textContent = original;
            h1.classList.remove('glitching');
        }, 750);

        setTimeout(triggerGlitch, 5000 + Math.random() * 6000);
    }

    setTimeout(triggerGlitch, 3000);
})();
