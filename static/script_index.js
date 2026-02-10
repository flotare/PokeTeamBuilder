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
            let path = "";
            if (input.id === "search_pokemon") {
                path = "pokemon";
            } else if (input.id === "search_items") {
                path = "objet";
            }

            // Crée la partie droite avec le bon nombre d'images
            let imagesHTML = `<img src="https://picsum.photos/80" width="40">`;
            if (path === "pokemon") {
                imagesHTML += `<img src="https://picsum.photos/81" width="40">`;
                imagesHTML += `<img src="https://picsum.photos/82" width="40">`;
            }

            div.innerHTML = `
                <div class="left">
                    
                    <a class="left" href="/${path}/${encodeURIComponent(item.name)}">${item.name}</a>
                </div>
                <div class="right">
                    ${imagesHTML}
                </div>
            `;

            resultsDiv.appendChild(div);
        });
    });
}


setupSearch("search_pokemon", "results_pokemon", "/search/pokemon");
setupSearch("search_items", "results_items", "/search/objet");