# Poster video

Turns a system poster into a 16-second vertical short (1080×1920, 30 fps, no sound) for TikTok, YouTube Shorts and X. Add music in the app.

Four scenes: close-up on the people, pan to the machine, the full poster (labeled *Concept art* with its tech tree ID), then the OASA end card with joinoasa.org/join.

## Run it

```
cd tools/poster-video
npm install @fontsource/sora@5.2.5 --no-save   # Sora font files
pip install pillow                             # needs ffmpeg and the Inter font too
python3 poster_video.py configs/l6-disaster-blimp.json --frames   # check frames only
python3 poster_video.py configs/l6-disaster-blimp.json            # full render
```

`--frames` writes four check frames to `<out>.parts/`. Look at them before a full render.

## Add a poster

1. Put the poster in [`posters/systems/`](../../posters/systems/) (4:5, people in the lower third, the machine in the upper half, headline at the bottom).
2. Copy a config in `configs/` and change:
   - `closeup` and `hero`: where the camera starts and ends, as fractions of the poster (`cx`, `cy`) and a crop width in pixels (`w`). Keep both crops above the poster's headline.
   - `hook`, `line2`, `line3`, `end`: caption lines. Start a line with `*` for gold.
   - `badge`: always *Concept art* plus the tech tree ID, until the system is real.
3. Run `--frames`, adjust, then render.
