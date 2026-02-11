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

applyStatBars();
