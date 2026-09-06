# Fourier en images

Une page en français consacrée au portrait de Mika reconstruit par addition de composantes de Fourier.

## Ouvrir et mettre en ligne

Ouvrir `index.html` dans un navigateur. La page fonctionne directement sur disque, sans installation.

Pour la publier, uploader le contenu de ce dossier sur un hébergement statique en conservant l’arborescence. `index.html` est la page d’entrée. Les chemins des ressources sont relatifs : le site peut aussi être placé dans un sous-dossier.

Tous les médias, styles et scripts nécessaires sont inclus. Aucun CDN, police distante, analyse d’audience, cookie ou appel à une API n’est nécessaire. Les liens documentaires ouvrent des sites externes uniquement lorsqu’on les suit. Le JavaScript sert aux curseurs et au passage entre GIF et image fixe ; l’article et le GIF restent accessibles sans lui. La préférence système de réduction des animations affiche une image fixe lorsque JavaScript est actif.

Le GIF initial est conservé intégralement : 66 421 222 octets, soit 66,4 Mo. Il représente l’essentiel du poids du site et peut demander un peu de temps à charger sur une connexion lente. La page permet de le télécharger et d’afficher une image fixe.

## Fichiers

- `index.html`, `style.css`, `app.js` : page, présentation et expérience interactive.
- `assets/portrait-fourier.gif` : animation initiale de 205 images, durée 25,15 secondes.
- `assets/animation-apercu.png` : image fixe du dernier état du GIF.
- `assets/reference-gris.png` : référence du calcul, 384 × 384 pixels.
- `assets/etapes-fourier.png` : six étapes de la reconstruction.
- `calcul/create_fourier_gif.py` : version portable du script utilisé pour produire l’animation.
- `calcul/requirements.txt` : versions des bibliothèques utilisées.
- `calcul/fourier-stats.json` : mesures de l’exécution originale ; chemin source remplacé par le chemin relatif de la référence distribuée.
- `calcul/fonts/` : polices Liberation Sans et licence OFL pour reproduire le rendu.

## Recalculer

Python 3.12 ou plus récent est recommandé pour les versions de bibliothèques fixées ici.

Depuis ce dossier :

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r calcul/requirements.txt
python calcul/create_fourier_gif.py
```

Sous Windows PowerShell, activer l’environnement avec `.venv\Scripts\Activate.ps1` à la place de la commande `source`.

Le script utilise la référence déjà convertie en gris, recadrée et réduite. La photo webcam entière n’est pas requise. Les résultats sont créés dans `resultats/`, sans modifier les médias de la page. Les polices sont incluses : aucun chemin système propre à la machine d’origine n’est nécessaire. Il faut quelques centaines de mégaoctets de mémoire pour conserver les images avant l’encodage.

Préparation originale : photo 1 280 × 720, conversion Pillow en `L`, recadrage `(340, 0, 1060, 720)`, puis réduction Lanczos à 384 × 384. Le calcul utilise la DFT 2D normalisée, regroupe les conjugués, et trie les contributions par énergie décroissante.

Le script contrôle l’identité finale des pixels, la décroissance de l’erreur quadratique et la lecture du GIF produit. Le fichier GIF original est inchangé ; le script portable inclut une correction du singulier « 1 motif » dans la planche des étapes.

## Sources et crédits

Photo : Mika. Expérience et page réalisées avec l’aide d’un assistant en septembre 2026. Les explications renvoient directement aux documentations NumPy, Pillow et SciPy, au cours JPEG de Queen’s University, à Analog Devices et au chapitre de Lugauer et Wetzl sur l’IRM.

Les sources et médias de ce dossier permettent de partager et de reproduire cette expérience. Aucune licence supplémentaire n’est imposée ici à la photo de Mika. Les polices incluses conservent leur licence propre dans `calcul/fonts/LICENSE.txt`.
