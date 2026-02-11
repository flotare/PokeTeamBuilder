function applyStatBars() {
  const max = 255;

  document.querySelectorAll(".stat-bar").forEach(bar => {
    const stat = Number(bar.dataset.stat);

    const clamped = Math.max(0, Math.min(stat, max));
    const percent = (clamped / max) * 100;
    const hue = (clamped / max) * 120;

    bar.style.width = percent + "%";
    bar.style.background =
      `linear-gradient(90deg, hsl(${hue},80%,45%), hsl(${hue},80%,60%))`;
  });
}


document.addEventListener("DOMContentLoaded", () => {

    applyStatBars();

    const addBtn = document.getElementById("add-to-team-btn");
    if (addBtn) {
        addBtn.addEventListener("click", () => {
            const pokemon = {
                name: addBtn.dataset.name,
                img: addBtn.dataset.img
            };

            const data = sessionStorage.getItem("poketeam");
            let team = data ? JSON.parse(data) : Array(6).fill(null);

            const emptyIndex = team.findIndex(slot => slot === null);
            if (emptyIndex === -1) {
                alert("La team est pleine !");
                return;
            }

            team[emptyIndex] = pokemon;
            sessionStorage.setItem("poketeam", JSON.stringify(team));
            alert(`${pokemon.name} ajouté à la team !`);
        });
    }

});