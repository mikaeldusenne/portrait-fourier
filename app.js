"use strict";

// Everything runs locally; the page needs no server, libraries, or network API.
const portrait = document.getElementById("portrait-animation");
const toggle = document.getElementById("toggle-animation");
const status = document.getElementById("player-status");
const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");
let animated = !motionPreference.matches;

function showPortrait() {
  portrait.src = animated ? "assets/portrait-fourier.gif" : "assets/animation-apercu.png";
  portrait.alt = animated
    ? "Animation : des motifs rayés, puis des groupes de motifs, s’ajoutent à gauche tandis que leur somme fait apparaître le portrait de Mika à droite."
    : "Dernière image de la reconstruction : le portrait de Mika est complet, après l’ajout de 73 729 motifs.";
  toggle.textContent = animated ? "Voir l’image fixe" : "Voir l’animation";
  status.textContent = animated ? "25 secondes · lecture en boucle" : "Image fixe · reconstruction complète";
}
toggle.hidden = false;
showPortrait();
toggle.addEventListener("click", () => { animated = !animated; showPortrait(); });
motionPreference.addEventListener("change", (event) => { animated = !event.matches; showPortrait(); });
portrait.addEventListener("error", () => {
  status.textContent = "Image indisponible. Vérifiez que le dossier assets accompagne la page.";
});

const canvas = document.getElementById("wave-canvas");
const context = canvas.getContext("2d");
const controls = Object.fromEntries(["u", "v", "a", "p"].map((key) => [key, document.getElementById(`wave-${key}`)]));

function drawWave() {
  if (!context) return;
  const values = Object.fromEntries(Object.entries(controls).map(([key, control]) => [key, Number(control.value)]));
  const { u, v, a, p } = values;
  const phase = p * Math.PI / 180;
  const { width, height } = canvas;
  const pixels = context.createImageData(width, height);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const level = Math.round(128 + a * Math.cos(2 * Math.PI * (u * x / width + v * y / height) + phase));
      const offset = 4 * (y * width + x);
      pixels.data[offset] = pixels.data[offset + 1] = pixels.data[offset + 2] = level;
      pixels.data[offset + 3] = 255;
    }
  }
  context.putImageData(pixels, 0, 0);
  for (const [key, value] of Object.entries(values)) {
    document.getElementById(`value-${key}`).value = `${value}${key === "p" ? "°" : ""}`;
  }
  const summary = `u = ${u} · v = ${v} · A = ${a} · φ = ${p}°`;
  document.getElementById("wave-summary").textContent = summary;
  canvas.setAttribute("aria-label", `Motif sinusoïdal : fréquence horizontale ${u}, verticale ${v}, amplitude ${a}, phase ${p} degrés.`);
}
for (const control of Object.values(controls)) control.addEventListener("input", drawWave);
for (const button of document.querySelectorAll(".presets button")) {
  button.addEventListener("click", () => {
    controls.u.value = button.dataset.u;
    controls.v.value = button.dataset.v;
    controls.a.value = "90";
    controls.p.value = "0";
    drawWave();
  });
}
drawWave();
