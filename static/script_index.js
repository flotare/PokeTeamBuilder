const input_pokemon = document.getElementById("search_pokemon");
const input_items = document.getElementById("search_items");
const resultsDiv = document.getElementById("results");

async function setupSearch(inputId, resultId, endpoint) {
    const input = document.getElementById(inputId);
    const resultsDiv = document.getElementById(resultId);

    input.addEventListener("input", async () => {
        const q = input.value;
        if (!q) {
            resultsDiv.innerHTML = "";
            return;
        }

        const res = await fetch(`${endpoint}?q=${q}`);
        const data = await res.json();

        resultsDiv.innerHTML = "";

        data.forEach(item => {
            const div = document.createElement("div");
            div.className = "result";

            // Détermine le type pour construire l'URL
            let path = input.id === "search_pokemon" ? "pokemon" : "objet";

            // HTML gauche (nom poké/objet + hyperlien)
            let leftHTML = `<a class="left" href="/${path}/${encodeURIComponent(item.name)}">${item.name}</a>`;


            // HTML droit (images)

            // Crée la partie droite avec le bon nombre d'images
            let imagesHTML = "";

            if (path === "pokemon") {

                let typesHTML = "";

                if (item.types && item.types.length > 0) {
                    item.types.forEach(type => {
                        typesHTML += `<img src="${type.type_img}" width="80">`;
                    });
                }

                imagesHTML = `
                    <img class="pokemon-img" src="${item.img}" width="80">
                    <div class="types">
                        ${typesHTML}
                    </div>
                `;

            } else if (path === "objet") {
                imagesHTML = `<img src="${item.img}" width="80">`;
            }

            div.innerHTML = `
                <div class="left">${leftHTML}</div>
                <div class="right">${imagesHTML}</div>
            `;

            resultsDiv.appendChild(div);
        });
    });
}


setupSearch("search_pokemon", "results_pokemon", "/search/pokemon");
setupSearch("search_items", "results_items", "/search/objet");