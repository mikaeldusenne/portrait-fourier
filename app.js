"use strict";

// Everything runs locally; the page needs no server, libraries, or network API.
const portrait = document.getElementById("portrait-animation");
const still = document.getElementById("portrait-still");
const toggle = document.getElementById("toggle-animation");
const status = document.getElementById("player-status");
const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");
let animated = !motionPreference.matches;

function showPortrait() {
  if (!animated) portrait.pause();
  portrait.hidden = !animated;
  still.hidden = animated;
  toggle.textContent = animated ? "Voir l’image fixe" : "Voir la vidéo";
  status.textContent = animated
    ? "25,15 secondes · lecture à la demande"
    : "Image fixe · reconstruction complète";
}
toggle.hidden = false;
showPortrait();
toggle.addEventListener("click", () => { animated = !animated; showPortrait(); });
motionPreference.addEventListener("change", (event) => { animated = !event.matches; showPortrait(); });
portrait.addEventListener("play", () => { status.textContent = "Lecture · utilisez les commandes pour faire pause ou revenir en arrière"; });
portrait.addEventListener("pause", () => {
  if (animated) status.textContent = "En pause · choisissez une étape avec la barre de lecture";
});
portrait.addEventListener("ended", () => { status.textContent = "Reconstruction complète · relancez la vidéo pour revoir les étapes"; });
function videoError() {
  status.textContent = "Vidéo indisponible. Vous pouvez télécharger le MP4 ou afficher l’image fixe.";
}
portrait.addEventListener("error", videoError);
portrait.querySelector("source").addEventListener("error", videoError);

const canvas = document.getElementById("wave-canvas");
const context = canvas.getContext("2d");
const sumCanvas = document.getElementById("sum-canvas");
const sumContext = sumCanvas.getContext("2d");
const controls = Object.fromEntries(["u", "v", "a", "p"].map((key) => [key, document.getElementById(`wave-${key}`)]));
const sum = new Float64Array(sumCanvas.width * sumCanvas.height).fill(128);
const addedWaves = [];
const undoWave = document.getElementById("undo-wave");
const resetWaves = document.getElementById("reset-waves");

function currentWave() {
  return Object.fromEntries(Object.entries(controls).map(([key, control]) => [key, Number(control.value)]));
}

function waveValue({ u, v, a, p }, x, y, width, height) {
  return a * Math.cos(2 * Math.PI * (u * x / width + v * y / height) + p * Math.PI / 180);
}

function grayPixel(pixels, index, value) {
  const level = Math.round(Math.max(0, Math.min(255, value)));
  const offset = 4 * index;
  pixels.data[offset] = pixels.data[offset + 1] = pixels.data[offset + 2] = level;
  pixels.data[offset + 3] = 255;
}

function drawWave() {
  if (!context) return;
  const values = currentWave();
  const { u, v, a, p } = values;
  const { width, height } = canvas;
  const pixels = context.createImageData(width, height);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      grayPixel(pixels, y * width + x, 128 + waveValue(values, x, y, width, height));
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

function drawSum() {
  if (!sumContext) return;
  const pixels = sumContext.createImageData(sumCanvas.width, sumCanvas.height);
  let clipped = 0;
  for (let index = 0; index < sum.length; index++) {
    grayPixel(pixels, index, sum[index]);
    if (sum[index] < 0 || sum[index] > 255) clipped++;
  }
  sumContext.putImageData(pixels, 0, 0);
  const count = addedWaves.length;
  const label = `${count} ${count > 1 ? "ondes ajoutées" : "onde ajoutée"}`;
  document.getElementById("sum-status").textContent = count ? label : `${label} · gris de départ`;
  sumCanvas.setAttribute("aria-label", `Image cumulée : gris de départ plus ${label}.`);
  document.getElementById("sum-clipping").textContent = clipped
    ? `${(100 * clipped / sum.length).toLocaleString("fr-FR", { maximumFractionDigits: 1 })} % de l’image dépasse les gris affichables : ces zones apparaissent blanches ou noires. Leurs contributions restent conservées pour les prochains ajouts.`
    : "Chaque ajout conserve toute sa contribution, même dans les zones devenues blanches ou noires.";
  undoWave.disabled = resetWaves.disabled = count === 0;
}

function accumulate(wave, direction) {
  const { width, height } = sumCanvas;
  // Keep the full signed sum: clipping here would prevent waves from cancelling.
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      sum[y * width + x] += direction * waveValue(wave, x, y, width, height);
    }
  }
}

document.getElementById("add-wave").addEventListener("click", () => {
  const wave = currentWave();
  addedWaves.push(wave);
  accumulate(wave, 1);
  drawSum();
});
undoWave.addEventListener("click", () => {
  const wave = addedWaves.pop();
  if (!wave) return;
  accumulate(wave, -1);
  if (!addedWaves.length) sum.fill(128);
  drawSum();
});
resetWaves.addEventListener("click", () => {
  addedWaves.length = 0;
  sum.fill(128);
  drawSum();
});
for (const control of Object.values(controls)) control.addEventListener("input", drawWave);
for (const button of document.querySelectorAll(".presets button")) {
  button.addEventListener("click", () => {
    controls.u.value = button.dataset.u;
    controls.v.value = button.dataset.v;
    drawWave();
  });
}
drawWave();
drawSum();
document.getElementById("wave-inputs").disabled = !context || !sumContext;
