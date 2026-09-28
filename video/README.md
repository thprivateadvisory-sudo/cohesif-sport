# Pub vidéo Cohesif Sport (9:16, 36 s)

| Fichier | Contenu |
|---|---|
| `cohesif-sport-pub.mp4` | Version finale : voix off, musique, sous-titres incrustés |
| `cohesif-sport-pub-sans-voix.mp4` | Même montage, musique seule (pour enregistrer une autre voix par-dessus) |
| `sous-titres.srt` | Sous-titres seuls, par phrases, pour Instagram / TikTok / YouTube |
| `source/` | Fichiers qui génèrent la vidéo (animation HTML, voix, musique) |

## Texte de la voix off

À lire posément, ton direct et complice, ~36 s.

> Président de club ? … Stop.
> Vous passez vos soirées sur les licences, les dossiers, les relances…
> Et pendant ce temps, votre club laisse des milliers d'euros de subventions sur la table.
> Cohesif Sport gère votre club de A à Z : l'administratif, les subventions, l'Academy, les terrains… et même votre facture d'énergie.
> On commence par un audit gratuit. On construit un plan sur mesure. Et ensuite, on gère. Vous, vous jouez.
> Clubs amateurs, mairies, districts : partout en France.
> Seulement quatre places pour la saison 2026.
> Cohesif Sport. Demandez votre audit gratuit sur cohesifsport.fr.

## Régénérer la vidéo

Prérequis : Python 3 (`kokoro-onnx soundfile scipy`), Node + Playwright, ffmpeg,
et le modèle Kokoro (`kokoro-v1.0.onnx`, `voices-v1.0.bin`, releases GitHub de
thewh1teagle/kokoro-onnx).

```sh
cd video/source
npm install
python3 tts.py       # voix off + timeline.json + sous-titres.srt
python3 audio.py     # musique, effets, mixage -> mix.wav
node render.js full  # rendu image par image -> video.mp4
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy \
  -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -shortest ../cohesif-sport-pub.mp4
```

Le texte (voix + sous-titres) se modifie dans `script.py` ; les mots entre
`*astérisques*` sont surlignés en or dans les sous-titres.
