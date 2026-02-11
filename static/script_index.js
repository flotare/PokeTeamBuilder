const input_pokemon = document.getElementById("search_pokemon");
const input_items = document.getElementById("search_items");
const resultsDiv = document.getElementById("results");


const MAX_TEAM = 6;
let team = Array(MAX_TEAM).fill(null);

// Fonction pour ajouter un Pokémon à la team
function addToTeam(pokemon) {
    const emptyIndex = team.findIndex(slot => slot === null);
    if (emptyIndex === -1) {
        alert("La team est pleine !");
        return;
    }
    team[emptyIndex] = pokemon;
    saveTeam();
    renderTeam();
}

// Fonction pour retirer un Pokémon de la team
function removeFromTeam(index) {
    team[index] = null;
    saveTeam();
    renderTeam();
}

// Mise à jour de l'affichage de la team
function renderTeam() {
    const slots = document.querySelectorAll(".team-slot");
    slots.forEach((slot, idx) => {
        slot.innerHTML = "";
        if (team[idx]) {
            slot.classList.add("filled");
            slot.innerHTML = `
                <img src="${team[idx].img}" alt="${team[idx].name}">
                <div>${team[idx].name}</div>
                <button class="remove-btn">-</button>
            `;
            slot.querySelector(".remove-btn").addEventListener("click", () => removeFromTeam(idx));
        } else {
            slot.classList.remove("filled");
            slot.innerHTML = `<div class="team-empty">Vide</div>`;
        }
    });
}

function saveTeam() {
    sessionStorage.setItem("poketeam", JSON.stringify(team));
}

function loadTeam() {
    const data = sessionStorage.getItem("poketeam");
    if (data) {
        try {
            const saved = JSON.parse(data);
            if (Array.isArray(saved)) {
                team = saved;
            }
        } catch (e) {
            console.error("Erreur parsing team:", e);
        }
    }
}



// --- Recherches Pokémon et objets (existant) ---
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


// Initial render
loadTeam();
renderTeam();