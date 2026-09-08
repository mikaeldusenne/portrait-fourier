# Fourier en images

Un portrait reconstruit par addition d’ondes sinusoïdales en 2D, avec une page pédagogique en français et le code Python reproductible.

- [Voir la page](https://mikaeldusenne.github.io/portrait-fourier/)
- [Code source](https://github.com/mikaeldusenne/portrait-fourier)

## Ce qui s’ajoute

La luminosité moyenne constitue le point de départ. Chaque composante élémentaire est une sinusoïde spatiale, définie par sa fréquence horizontale et verticale, son amplitude et sa phase. Les coefficients conjugués sont regroupés pour produire une onde réelle. Les 73 729 ondes sont classées par énergie décroissante.

Les 40 premières ondes arrivent une par une ; ensuite, les ajouts se font par groupes croissants pour garder une animation courte. Le panneau gauche montre alors **la somme de plusieurs ondes**, avec un contraste amplifié. Son aspect brouillé en fin d’animation vient de cette superposition. Le panneau droit montre leur somme cumulée à son intensité réelle.

## Voir la vidéo

Ouvrir `index.html` dans un navigateur, ou servir le dossier :

```sh
python -m http.server 8000
```

Puis ouvrir http://localhost:8000. Aucun build, CDN, cookie ni API n’est nécessaire. La vidéo MP4 H.264 mesure 1 000 × 750 pixels, dure 25,15 secondes et pèse environ **6,6 Mo**, contre 66,4 Mo pour le GIF initial. Les commandes natives permettent la lecture, la pause, le déplacement dans le temps et le plein écran. La lecture démarre à la demande. Avec une préférence de réduction des animations, l’image fixe est affichée par défaut ; la vidéo reste accessible.

La vidéo et l’article fonctionnent sans JavaScript. Le script de la page ajoute le choix entre vidéo et PNG ainsi que le petit laboratoire d’ondes.

## Fichiers

- `index.html`, `style.css`, `app.js` : page et laboratoire interactif.
- `assets/portrait-fourier.mp4` : vidéo générée directement depuis les états calculés.
- `assets/animation-apercu.png` : dernière étape, sans perte.
- `assets/reference-gris.png` : référence du calcul, 384 × 384 pixels.
- `assets/etapes-fourier.png` : six étapes de la reconstruction.
- `calcul/create_fourier_video.py` : calcul, rendu, encodage et vérifications.
- `calcul/requirements.txt` : dépendances Python fixées.
- `calcul/fourier-stats.json` : mesures du calcul et de la vidéo publiée.
- `calcul/fonts/` : polices Liberation Sans et licence OFL.

Le GIF initial est exclu du dépôt pour conserver un téléchargement léger. Le générateur permet de recréer une version GIF avec les annotations actualisées.

## Recalculer

Installer Python 3.12 ou plus récent et [FFmpeg](https://ffmpeg.org/download.html), avec `ffmpeg` et `ffprobe` sur le PATH et l’encodeur `libx264` disponible.

Depuis la racine du dépôt :

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r calcul/requirements.txt
python calcul/create_fourier_video.py
```

Sous Windows PowerShell, utiliser `.venv\Scripts\Activate.ps1` pour activer l’environnement.

Les sorties sont écrites dans `resultats/`, sans modifier les médias de la page. Pour mettre à jour la page, recopier `portrait-fourier.mp4`, `animation-apercu.png` et `etapes-fourier.png` dans `assets/`, puis `fourier-stats.json` dans `calcul/` ; actualiser aussi le poids affiché si nécessaire. Pour produire également un GIF :

```sh
python calcul/create_fourier_video.py --gif
```

Le script repart de la référence préparée, sans nécessiter la photo webcam entière. Préparation originale : photo 1 280 × 720, conversion Pillow en `L`, recadrage `(340, 0, 1060, 720)`, réduction Lanczos à 384 × 384. Les polices sont incluses. Prévoir quelques centaines de mégaoctets de mémoire.

Les 205 états sont maintenus à l’écran pendant leur durée originale, sur une base de 100 images/s pour conserver exactement les pas de 10 ms. Les répétitions ne rajoutent aucune onde ni interpolation. L’encodage utilise H.264, CRF 16, YUV 4:2:0 et `faststart` pour la lecture web. Le binaire peut varier selon la version de FFmpeg.

## Vérifications

Le générateur contrôle la couverture du spectre, l’énergie (Parseval), la concordance de trois composantes isolées avec leur formule en cosinus, la réalité de la reconstruction et la décroissance de l’erreur quadratique. L’erreur finale maximale du calcul est de **1,71 × 10⁻¹³** niveau de gris ; après arrondi, les pixels sont identiques à la référence.

Cette identité concerne le calcul et le PNG. Le MP4 utilise une compression avec pertes : le script décode toute la vidéo, vérifie sa durée, son format et son nombre d’images, puis mesure l’erreur du portrait final. Sur la vidéo publiée, son erreur quadratique moyenne en racine vaut **1,42 niveau de gris sur 255** (seuil de contrôle : 2). Avec `--gif`, le script contrôle aussi la durée et l’identité du panneau final du GIF.

## Publication

La page HTML et ses ressources vivent dans ce même dépôt. GitHub Pages sert la racine de la branche `feat/video-github`. `.nojekyll` permet de servir les fichiers statiques directement. Un autre hébergement statique convient aussi : les chemins de ressources sont relatifs.

## Sources et crédits

Photo : Mika. Expérience réalisée avec l’aide d’un assistant en septembre 2026. Les références documentaires sont liées dans la page, notamment [NumPy](https://numpy.org/doc/stable/reference/routines.fft.html) et [FFmpeg](https://ffmpeg.org/ffmpeg.html).

Aucune licence supplémentaire n’est imposée ici à la photo. Les polices incluses conservent leur licence propre dans `calcul/fonts/LICENSE.txt`.
