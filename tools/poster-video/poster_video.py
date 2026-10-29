"""Poster -> 9:16 short (1080x1920, 30 fps, no audio).

Usage: python3 poster_video.py configs/<name>.json [--frames]   (--frames: only write check frames)
Scenes: closeup push -> pan to hero -> full poster -> end card. Each scene is its own
encoded file with its crossfade inside; files are joined with the concat demuxer.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '../..'))
FONTS = os.environ.get('SORA_DIR', os.path.join(HERE, 'node_modules/@fontsource/sora/files'))
SORA = lambda w, s: ImageFont.truetype(f'{FONTS}/sora-latin-{w}-normal.woff', s)
INTER = lambda s: ImageFont.truetype(os.environ.get('INTER_FONT', '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'), s)
NAVY, GOLD, CREAM = (11, 37, 58), (227, 163, 44), (250, 243, 228)
LOGO = os.path.join(REPO, 'logos/oasa-logo/png/oasa-logo-vertical-on-dark.png')
XF = 0.5  # crossfade seconds

cfg = json.load(open(sys.argv[1]))
poster = Image.open(os.path.join(REPO, cfg['poster'])).convert('RGB')
PW, PH = poster.size

def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t

# Blurred, darkened backdrop for the full-poster scene.
def cover(img, w, h):
    s = max(w / img.width, h / img.height)
    im = img.resize((round(img.width * s), round(img.height * s)), Image.BICUBIC)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))
BACK = Image.blend(cover(poster, W, H).filter(ImageFilter.GaussianBlur(40)), Image.new('RGB', (W, H), NAVY), 0.45)

def window(cx, cy, ww):
    """9:16 crop of the poster centred on (cx, cy) in poster fractions, ww = width in poster px."""
    wh = ww * 16 / 9
    if wh > PH: wh = PH; ww = wh * 9 / 16
    x0 = min(max(cx * PW - ww / 2, 0), PW - ww); y0 = min(max(cy * PH - wh / 2, 0), PH - wh)
    return poster.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + ww, y0 + wh))

def shade(im, top=0.55, bottom=0.0):
    """Dark gradient at the top (and optionally bottom) so text reads."""
    g = Image.new('L', (1, H))
    for y in range(H):
        a = max(top * (1 - y / 760), 0) if y < 760 else 0
        if bottom and y > H - 700: a = max(a, bottom * (y - (H - 700)) / 700)
        g.putpixel((0, y), int(255 * a))
    im.paste(Image.new('RGB', (W, H), (6, 18, 30)), (0, 0), g.resize((W, H)))
    return im

def text_block(im, lines, y, alpha, size=78, color=CREAM, font=None, gap=18):
    """Centered lines with a soft shadow; alpha 0..1 also slides it up slightly."""
    if alpha <= 0: return im
    if font is None:
        font = SORA(800, size)
        widest = max(ImageDraw.Draw(Image.new('L', (1, 1))).textlength(l.lstrip('*'), font=font) for l in lines)
        if widest > 960: font = SORA(800, int(size * 960 / widest))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    y += round((1 - alpha) * 30)
    for ln in lines:
        c = GOLD if ln.startswith('*') else color; ln = ln.lstrip('*')
        bw = d.textlength(ln, font=font); x = (W - bw) / 2
        d.text((x, y), ln, font=font, fill=c + (round(255 * alpha),))
        y += font.size + gap
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.putalpha(layer.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 0.8))
    im = im.convert('RGBA'); im.alpha_composite(sh, (0, 4)); im.alpha_composite(layer)
    return im.convert('RGB')

def fade(t, start, dur=0.6): return ease((t - start) / dur)

# Scene durations (s)
S = cfg.get('durations', [3.5, 4.0, 4.0, 4.5])

def scene1(t):  # close-up push on the human moment
    a = cfg['closeup']; k = ease(t / S[0])
    im = window(a['cx'], lerp(a['cy'], a['cy'] - 0.01, k), lerp(a['w'], a['w'] * 0.9, k))
    return text_block(shade(im), cfg['hook'], 250, fade(t, 0.3))

def scene2(t):  # pan from the close-up up to the hero
    a, b = cfg['closeup'], cfg['hero']; k = ease(t / S[1])
    im = window(lerp(a['cx'], b['cx'], k), lerp(a['cy'], b['cy'], k), lerp(a['w'] * 0.9, b['w'], k))
    return text_block(shade(im), cfg['line2'], 250, fade(t, 0.8))

def scene3(t):  # full poster on the blurred backdrop, slow push
    k = ease(t / S[2]); s = lerp(W / PW * 0.96, W / PW * 1.02, k)
    pw, ph = round(PW * s), round(PH * s)
    im = BACK.copy(); im.paste(poster.resize((pw, ph), Image.BICUBIC), ((W - pw) // 2, 330 + (1350 - ph) // 2))
    im = text_block(im, cfg['line3'], 120, fade(t, 0.3), size=56)
    return text_block(im, [cfg.get('badge', 'Concept art')], 1760, fade(t, 0.6), font=INTER(30), color=(200, 210, 222))

LOGO_IM = Image.open(LOGO).convert('RGBA'); LOGO_IM = LOGO_IM.resize((560, round(LOGO_IM.height * 560 / LOGO_IM.width)), Image.LANCZOS)
def scene4(t):  # end card
    im = Image.blend(BACK, Image.new('RGB', (W, H), NAVY), 0.6).convert('RGBA')
    a = fade(t, 0.1); lg = LOGO_IM.copy(); lg.putalpha(lg.getchannel('A').point(lambda v: v * a))
    im.alpha_composite(lg, ((W - lg.width) // 2, 380 + round((1 - a) * 30))); im = im.convert('RGB')
    y = 380 + LOGO_IM.height + 110
    im = text_block(im, cfg['end'], y, fade(t, 0.6), size=64)
    return text_block(im, ['joinoasa.org/join'], y + 330, fade(t, 1.1), size=54, color=GOLD)

SCENES = [scene1, scene2, scene3, scene4]

def frame(i, t):
    im = SCENES[i](t)
    if i and t < XF:  # crossfade from the previous scene's last frame
        im = Image.blend(SCENES[i - 1](S[i - 1]), im, ease(t / XF))
    return im

out = cfg['out']; work = out + '.parts'; os.makedirs(work, exist_ok=True)
if '--frames' in sys.argv:
    for i, t in [(0, 2.5), (1, 3.5), (2, 3.0), (3, 3.0)]:
        frame(i, t).save(f'{work}/check-{i}.jpg', quality=90)
    sys.exit()

parts = []
for i, dur in enumerate(S):
    tmp, fin = f'{work}/s{i}.tmp.mp4', f'{work}/s{i}.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    for n in range(round(dur * FPS)):
        p.stdin.write(frame(i, n / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, fin)
    parts.append(fin)
with open(f'{work}/list.txt', 'w') as f: f.writelines(f"file '{os.path.abspath(x)}'\n" for x in parts)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{work}/list.txt', '-c', 'copy', '-movflags', '+faststart', out], check=True)
print('wrote', out)
