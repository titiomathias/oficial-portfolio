const url = "/reviews";

axios.get(url, {
    withCredentials: false,
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
}).then(function (response) {
    if (Array.isArray(response.data)) {
        const container = document.getElementById("result");

        response.data.forEach(function (item) {
            const article = document.createElement("article");
            article.className = "feedback c-carousel__slide";

            const a = document.createElement("a");
            try {
                const parsed = new URL(item.link);
                a.href = ["http:", "https:"].includes(parsed.protocol) ? item.link : "#";
            } catch {
                a.href = "#";
            }
            a.target = "_blank";
            a.rel = "noopener noreferrer";
            a.className = "feedback-title";

            const h3 = document.createElement("h3");
            h3.textContent = item.title;
            a.appendChild(h3);

            const div = document.createElement("div");
            div.className = "comment-container";

            const p = document.createElement("p");
            p.className = "comment";
            p.textContent = item.comment;
            div.appendChild(p);

            article.appendChild(a);
            article.appendChild(div);
            container.appendChild(article);
        });

        const $simpleCarousel = document.querySelector(".js-carousel--simple");

        if ($simpleCarousel) {
            new Glider($simpleCarousel, {
                slidesToShow: 1,
                draggable: true,
                dots: ".js-carousel--simple-dots",
                arrows: {
                    prev: "#glider-prev",
                    next: "#glider-next",
                },
                rewind: true,
                duration: 0.2,
                ease: "ease-in-out",
                scrollLock: true,
                scrollLockDelay: 0,
            });
        } else {
            console.error("Elemento .js-carousel--simple não encontrado.");
        }
    } else {
        console.log("Is not array")
    }
}).catch(function (error) {
    console.error("Erro:", error)
    if (error.response){
        console.error("Status:", error.response.status);
        console.error("Headers:", error.response.headers);
    }
});