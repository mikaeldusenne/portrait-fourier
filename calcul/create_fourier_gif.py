#!/usr/bin/env python3
"""Reconstruct the supplied portrait by adding actual 2D Fourier components.

Portable edition of the script used for the original animation.
Input: ../assets/reference-gris.png, already cropped and resized.
Output: ../resultats/. Fonts are bundled in ./fonts/.
Dependencies: numpy, Pillow (see requirements.txt).
"""

from pathlib import Path
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "resultats"
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = HERE.parent / "assets" / "reference-gris.png"
CROP = (340, 0, 1060, 720)
N = 384
SIZE = (1000, 750)
FONT_DIR = HERE / "fonts"
PALETTE = [channel for level in range(256) for channel in (level,) * 3]


def font(size, bold=False):
    name = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


FONTS = {key: font(size, bold) for key, size, bold in [
    ("title", 32, True), ("subtitle", 18, False),
    ("label", 15, True), ("detail", 22, True),
    ("body", 17, False), ("small", 15, False), ("number", 18, True),
]}


def fmt(value):
    return f"{value:,}".replace(",", " ")


def gray_image(array):
    return Image.fromarray(np.rint(np.clip(array, 0, 255)).astype(np.uint8))


reference = Image.open(SOURCE).convert("L")
assert reference.size == (N, N), "The supplied reference must be 384 by 384 pixels."
reference.save(OUT / "reference-gris.png")
target = np.asarray(reference, dtype=np.float64)
# Normalized coefficients: the real component of a conjugate pair is
# 2 |F[ky,kx]| cos(2 pi (kx*x + ky*y)/N + arg(F[ky,kx])).
spectrum = np.fft.fft2(target) / (N * N)
flat = spectrum.ravel()
indices = np.arange(1, N * N)
ky, kx = np.divmod(indices, N)
partners = ((-ky) % N) * N + ((-kx) % N)
canonical = indices <= partners
indices, partners = indices[canonical], partners[canonical]
energies = np.abs(flat[indices]) ** 2 * np.where(indices == partners, 1, 2)
order = np.argsort(-energies, kind="stable")
indices, partners, energies = indices[order], partners[order], energies[order]
total = len(indices)
energy_total = float(energies.sum())
cumulative_energy = np.concatenate(([0.0], np.cumsum(energies)))
assert len(set(indices.tolist() + partners.tolist() + [0])) == N * N
assert np.allclose(energy_total, target.var(), atol=1e-9)

# Independently verify that isolated conjugate pairs are indeed striped cosines.
yy, xx = np.mgrid[:N, :N]
cosine_errors = []
for rank in (0, 10, 100):
    index, partner = int(indices[rank]), int(partners[rank])
    row, col = divmod(index, N)
    signed_y = row if row <= N // 2 else row - N
    signed_x = col if col <= N // 2 else col - N
    isolated = np.zeros_like(spectrum)
    isolated.ravel()[index] = flat[index]
    isolated.ravel()[partner] = flat[partner]
    factor = 1 if index == partner else 2
    cosine = factor * abs(flat[index]) * np.cos(
        2 * np.pi * (signed_x * xx + signed_y * yy) / N + np.angle(flat[index])
    )
    error = float(np.max(np.abs(cosine - np.fft.ifft2(isolated).real * N * N)))
    assert error < 1e-9
    cosine_errors.append(error)


def render(reconstruction, addition, count, energy, batch=0, alpha=1.0, start=False):
    page = Image.new("L", SIZE, 248)
    draw = ImageDraw.Draw(page)
    draw.text((32, 27), "Ton portrait, somme d’ondes", font=FONTS["title"], fill=24)
    draw.text((33, 73), "Une photo reconstruite par addition de motifs sinusoïdaux.",
              font=FONTS["subtitle"], fill=91)
    draw.text((32, 114), "CE QUI S’AJOUTE", font=FONTS["label"], fill=78)
    draw.text((456, 114), "LE PORTRAIT RECONSTRUIT", font=FONTS["label"], fill=78)
    amplitude = float(np.max(np.abs(addition)))
    if amplitude > 1e-12:
        visible_addition = 127.5 + 117.5 * addition / amplitude
    else:
        visible_addition = np.full_like(addition, 127.5)
    page.paste(gray_image(visible_addition).resize((360, 360), Image.Resampling.LANCZOS),
               (32, 142))
    page.paste(gray_image(reconstruction).resize((512, 512), Image.Resampling.LANCZOS),
               (456, 142))
    draw.rectangle((31, 141, 392, 502), outline=215)
    draw.rectangle((455, 141, 968, 654), outline=215)
    if start:
        headline = "Au départ : un gris uniforme"
        line1 = "La luminosité moyenne de ta photo."
        line2 = "Les rayures vont ajouter les détails."
        value = f"Moyenne : {target.mean():.1f} / 255"
    elif batch == 1:
        headline = f"Motif {fmt(count)}"
        row, col = divmod(int(indices[count - 1]), N)
        fx = col if col <= N // 2 else col - N
        fy = row if row <= N // 2 else row - N
        line1 = f"Fréquence : ({fx}, {fy}) cycles / image"
        line2 = f"Ajout de l’onde : {round(alpha * 100)} %"
        value = f"Variation maximale : ± {amplitude:.2f} / 255"
    else:
        headline = f"+ {fmt(batch)} motifs"
        line1 = "Le panneau montre leur somme."
        line2 = "Les petites contributions s’accélèrent."
        value = f"Variation maximale : ± {amplitude:.2f} / 255"
    draw.text((32, 524), headline, font=FONTS["detail"], fill=24)
    draw.text((32, 562), line1, font=FONTS["body"], fill=72)
    draw.text((32, 587), line2, font=FONTS["body"], fill=72)
    draw.text((32, 620), value, font=FONTS["small"], fill=78)
    draw.text((32, 643), "Motif amplifié · clair : + / sombre : −", font=FONTS["small"], fill=95)
    label = f"{fmt(count)} / {fmt(total)} motifs"
    if count == total:
        label += " · reconstruction complète"
    draw.text((32, 675), label, font=FONTS["number"], fill=24)
    energy_label = f"{min(100, energy * 100):.2f} % de l’énergie des détails"
    draw.text((968, 676), energy_label, font=FONTS["body"], fill=72, anchor="ra")
    draw.rounded_rectangle((32, 709, 968, 716), radius=3, fill=222)
    if energy > 0:
        draw.rounded_rectangle((32, 709, 32 + round(936 * min(1, energy)), 716), radius=3, fill=52)
    indexed = Image.fromarray(np.asarray(page).copy())
    indexed = indexed.convert("P")
    indexed.putpalette(PALETTE)
    return indexed


partial = np.zeros_like(spectrum)
partial[0, 0] = spectrum[0, 0]
reconstruction = np.full_like(target, target.mean())
frames = []
durations = []
measurements = []
stages = []


def append_frame(recon, addition, count, energy, duration, **kwargs):
    error = float(np.sqrt(np.mean((target - recon) ** 2)))
    if measurements:
        assert error <= measurements[-1]["rmse"] + 1e-8
    measurements.append({"count": count, "energy_fraction": float(energy), "rmse": error})
    frames.append(render(recon, addition, count, energy, **kwargs))
    durations.append(duration)
    return error


append_frame(reconstruction, np.zeros_like(target), 0, 0, 1000, start=True)
stages.append((0, reconstruction.copy()))
previous = 0
targets = list(range(1, 41)) + np.unique(
    np.rint(np.geomspace(41, total, 140)).astype(int)
).tolist()
for count in targets:
    batch = count - previous
    before = reconstruction.copy()
    new_indices = indices[previous:count]
    new_partners = partners[previous:count]
    partial.ravel()[new_indices] = flat[new_indices]
    partial.ravel()[new_partners] = flat[new_partners]
    computed = np.fft.ifft2(partial) * N * N
    assert float(np.max(np.abs(computed.imag))) < 1e-8
    reconstruction = computed.real
    addition = reconstruction - before
    if count <= 8:
        # Only the weight of this Fourier component changes, never a photo crossfade.
        for alpha in (0.25, 0.5, 0.75, 1.0):
            energy = (cumulative_energy[previous] + alpha * alpha * energies[previous]) / energy_total
            append_frame(before + alpha * addition, alpha * addition, count, energy,
                         110, batch=batch, alpha=alpha)
    else:
        append_frame(reconstruction, addition, count, cumulative_energy[count] / energy_total,
                     160 if count <= 40 else 90, batch=batch)
    if count in (1, 8, 40) or (previous < 1000 <= count) or count == total:
        stages.append((count, reconstruction.copy()))
    previous = count

durations[-1] = 3000
max_error = float(np.max(np.abs(reconstruction - target)))
assert max_error < 1e-8
assert np.array_equal(np.asarray(gray_image(reconstruction)), np.asarray(reference))
gray_image(reconstruction).save(OUT / "portrait-fourier-final.png")
frames[-1].convert("RGB").save(OUT / "animation-apercu.png")
print(f"Calculated {total} real components, {len(frames)} frames; max error {max_error:.3g}.", flush=True)

# A shared identity grayscale palette preserves the photograph and avoids flicker.
gif_path = OUT / "portrait-fourier.gif"
frames[0].save(gif_path, save_all=True, append_images=frames[1:],
               duration=durations, loop=0, optimize=False, disposal=1)
with Image.open(gif_path) as gif:
    assert gif.size == SIZE
    actual_frames = gif.n_frames
    actual_duration = 0
    for index in range(actual_frames):
        gif.seek(index)
        gif.load()
        actual_duration += gif.info.get("duration", 0)
    # Verify the rendered GIF's last portrait is identical to the expected panel.
    final_panel = np.asarray(gif.convert("L").crop((456, 142, 968, 654)))
    expected_panel = np.asarray(reference.resize((512, 512), Image.Resampling.LANCZOS))
    assert np.array_equal(final_panel, expected_panel)
    assert actual_duration == sum(durations)

sheet = Image.new("L", (1000, 780), 248)
draw = ImageDraw.Draw(sheet)
for index, (count, stage) in enumerate(stages):
    x = 20 + (index % 3) * 330
    y = 18 + (index // 3) * 390
    sheet.paste(gray_image(stage).resize((310, 310), Image.Resampling.LANCZOS), (x, y))
    draw.text((x, y + 324), f"{fmt(count)} {'motif' if count == 1 else 'motifs'}", font=FONTS["detail"], fill=24)
    energy = cumulative_energy[count] / energy_total * 100
    draw.text((x, y + 354), f"{energy:.2f} % de l’énergie des détails", font=FONTS["small"], fill=78)
sheet.save(OUT / "etapes-fourier.png")

stats = {
    "source": "../assets/reference-gris.png", "original_crop_xyxy": CROP, "reference_size": [N, N],
    "transform": "Normalized numpy.fft.fft2, Hermitian pairs grouped as real sinusoidal patterns",
    "order": "Descending component energy, constant mean initialized separately",
    "stripe_components": total, "mean_level": float(target.mean()),
    "detail_energy": energy_total, "max_final_error_gray_levels": max_error,
    "isolated_cosine_verification_errors": cosine_errors,
    "gif_frames": actual_frames, "duration_ms": actual_duration,
    "gif_bytes": gif_path.stat().st_size,
    "all_frame_rmse_monotonic": True, "gif_final_panel_matches_reference": True,
    "frames": measurements,
}
(OUT / "fourier-stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
print(json.dumps({key: value for key, value in stats.items() if key != "frames"}, indent=2), flush=True)
