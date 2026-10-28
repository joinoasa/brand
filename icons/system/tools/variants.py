"""Builds the icon variants from the full-color icons.

Input colors may be CSS variables (var(--navy)) or the brand hex values.

For each full-color icon (SRC/<family>/<name>.svg) writes to OUT/<family>/:
  <name>.svg        full color, real hex colors (works outside browsers)
  <name>-dark.svg   full color for dark backgrounds
  <name>-mono.svg   one color (Deep Navy), details cut out as holes
  <name>-white.svg  same as mono, in white
Usage: python3 fix.py SRC OUT
"""
import copy, io, os, re, sys
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
BRAND = {'navy': '#0B253A', 'steel': '#253A66', 'gold': '#E3A32C', 'teal': '#2F968A', 'aluminum': '#E5E8ED'}
DARK = {**BRAND, 'navy': '#E5E8ED', 'steel': '#8FA4CC', 'aluminum': '#0B253A'}
INK = {'navy', 'steel'}
VAR = re.compile(r'var\(--([a-z]+)\)')
HEX = {v.lower(): k for k, v in BRAND.items()}

def key(value):
    """Brand color name for var(--navy) or #0B253A, else None."""
    m = VAR.fullmatch(value or '')
    return m.group(1) if m else HEX.get((value or '').lower())
S = 64

def tag(e): return e.tag.split('}')[-1]

def paints(e):
    return [k for a in ('fill', 'stroke') for k in [key(e.get(a))] if k]

def recolor(e, table):
    for a in ('fill', 'stroke'):
        k = key(e.get(a))
        if k: e.set(a, table[k])
    for c in e: recolor(c, table)

def mono_paint(e, value):
    for a in ('fill', 'stroke'):
        if key(e.get(a)): e.set(a, value)
    if e.get('fill') is None and tag(e) != 'g': e.set('fill', value)  # default fill is black
    for c in e: mono_paint(c, value)

def raster(elems):
    svg = ET.Element(f'{{{NS}}}svg', {'viewBox': f'0 0 {S} {S}', 'width': str(S * 2), 'height': str(S * 2)})
    for e in elems: svg.append(e)
    png = cairosvg.svg2png(bytestring=ET.tostring(svg))
    return Image.open(io.BytesIO(png)).getchannel('A')

def coverage(a, b=None):
    pa = a.load(); pb = b.load() if b else None
    w, h = a.size; n = hit = 0
    for y in range(h):
        for x in range(w):
            if pa[x, y] > 128:
                n += 1
                if pb and pb[x, y] > 128: hit += 1
    return n, hit

def svg_root(title, tid):
    root = ET.Element(f'{{{NS}}}svg', {'viewBox': f'0 0 {S} {S}', 'role': 'img', 'aria-labelledby': tid})
    t = ET.SubElement(root, f'{{{NS}}}title', {'id': tid}); t.text = title
    return root

def write(root, path):
    ET.indent(root, '  ')
    with open(path, 'w') as f: f.write(ET.tostring(root, encoding='unicode') + '\n')

def main(src, out):
    report = []
    for fam in sorted(os.listdir(src)):
        if not os.path.isdir(os.path.join(src, fam)): continue
        os.makedirs(os.path.join(out, fam), exist_ok=True)
        for fn in sorted(os.listdir(os.path.join(src, fam))):
            if not fn.endswith('.svg') or fn[:-4].endswith(('-mono', '-white', '-dark')): continue
            name = fn[:-4]
            tree = ET.parse(os.path.join(src, fam, fn)).getroot()
            title = tree.find(f'{{{NS}}}title').text.strip()
            shapes = [e for e in tree if tag(e) not in ('title', 'style', 'desc', 'metadata')]
            base = f'oasa-{fam}-{name}'

            for suffix, table, label in (('', BRAND, ''), ('-dark', DARK, ' (for dark backgrounds)')):
                root = svg_root(title + label, f'{base}{suffix}-title')
                for e in shapes:
                    c = copy.deepcopy(e); recolor(c, table); root.append(c)
                write(root, os.path.join(out, fam, f'{name}{suffix}.svg'))

            # Knockout: paint in order; an accent shape lying mostly on ink becomes a hole.
            mask_elems, ink_elems, holes = [], [], 0
            for e in shapes:
                kinds = paints(e)
                role = 'ink'
                if kinds and not (set(kinds) & INK) and ink_elems:
                    probe = copy.deepcopy(e); mono_paint(probe, '#000')
                    acc = [copy.deepcopy(x) for x in mask_elems]
                    n, hit = coverage(raster([probe]), raster(acc) if acc else None)
                    if n and hit / n > 0.4: role = 'paper'
                m = copy.deepcopy(e); mono_paint(m, '#fff' if role == 'ink' else '#000')
                mask_elems.append(m)
                # what has been drawn as ink so far (holes erase), for the next overlap test
                if role == 'ink': ink_elems.append(m)
                else: holes += 1
            for suffix, color in (('-mono', BRAND['navy']), ('-white', '#FFFFFF')):
                mid = f'{base}{suffix}-cut'
                root = svg_root(title, f'{base}{suffix}-title')
                defs = ET.SubElement(root, f'{{{NS}}}defs')
                mask = ET.SubElement(defs, f'{{{NS}}}mask', {'id': mid, 'maskUnits': 'userSpaceOnUse', 'x': '0', 'y': '0', 'width': str(S), 'height': str(S)})
                ET.SubElement(mask, f'{{{NS}}}rect', {'width': str(S), 'height': str(S), 'fill': '#000'})
                for m in mask_elems: mask.append(copy.deepcopy(m))
                ET.SubElement(root, f'{{{NS}}}rect', {'width': str(S), 'height': str(S), 'fill': color, 'mask': f'url(#{mid})'})
                write(root, os.path.join(out, fam, f'{name}{suffix}.svg'))
            report.append(f'{fam}/{name}: {holes} cut-outs')
    print('\n'.join(report))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
