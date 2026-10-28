"""Build OASA logo files: mark, wordmark, lockups, app icon. Run: python3 lockups.py OUTDIR"""
import re, sys, importlib.util
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
S='.'  # folder holding the generated SVGs and the Sora .ttf instances
OUT=sys.argv[1]
spec=importlib.util.spec_from_file_location('word',f'{S}/word.py'); W=importlib.util.module_from_spec(spec); spec.loader.exec_module(W)
NAVY='#0B253A'; WHITE='#FFFFFF'; BLACK='#000000'
f600=TTFont(f'{S}/sora600.ttf'); g6=f600.getGlyphSet(); c6=f600.getBestCmap(); h6=f600['hmtx']

def caps(text, track=180):
    """Letterspaced caps as one path (y-down, cap top at 0, cap height 700)."""
    x=0; ds=[]
    for ch in text:
        g=c6[ord(ch)]
        if ch!=' ':
            pen=SVGPathPen(g6); g6[g].draw(TransformPen(pen,(1,0,0,-1,x,700))); ds.append(pen.getCommands())
        x+=h6[g][0]+track
    return ' '.join(ds), x-track

def mark_inner(variant):
    """The mark's SVG body with ids made unique for embedding."""
    s=open(f'{S}/{variant}.svg').read()
    body=re.sub(r'^.*?<title[^>]*>.*?</title>','',s,flags=re.S).rsplit('</svg>',1)[0]
    tag=variant.replace('oasa-','')
    for i in ['hz','in-upper','cut']: body=body.replace(f'id="{i}"',f'id="{tag}-{i}"').replace(f'url(#{i})',f'url(#{tag}-{i})')
    return body

WD,WW,WH=W.word()  # wordmark path, width, height (cap 0..730 + overshoot)
def wordmark(x,y,h,fill):
    s=h/730
    return f'<path transform="translate({x:.1f} {y:.1f}) scale({s:.5f})" fill="{fill}" stroke="{fill}" stroke-width="{W.EMBOLDEN}" stroke-linejoin="miter" d="{WD}"/>'
def mark(x,y,size,variant):
    return f'<svg x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" viewBox="0 0 512 512">{mark_inner(variant)}</svg>'
def doc(w,h,title,body,bg=None):
    rect=f'<rect width="{w:.0f}" height="{h:.0f}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{title}">\n<title>{title}</title>\n{rect}{body}\n</svg>\n'
# The mark's art spans y 40..330 and x 39..473 inside its 512 box.
def vertical(title, mv, ink, sub):
    W_=1000; wh=190; ww=WW*wh/730
    m=ww*0.84*512/434; mx=(W_-m)/2; my=-m*40/512+20   # mark art about 84% of the wordmark width
    wy=my+m*330/512+56
    d,tw=caps('OPEN AUTONOMOUS SYSTEMS ALLIANCE'); ts=ww/tw*0.98; ty=wy+wh+48
    body=mark(mx,my,m,mv)+wordmark((W_-ww)/2,wy,wh,ink)+f'<path transform="translate({(W_-tw*ts)/2:.1f} {ty:.1f}) scale({ts:.5f})" fill="{sub}" d="{d}"/>'
    return W_, ty+700*ts+30, title, body
def horizontal(title, mv, ink, sub):
    m=400; mx=10-m*39/512; my=-m*40/512+10; art_h=m*290/512
    wh=art_h*0.62; ww=WW*wh/730; wx=mx+m*473/512+40; wy=10
    d1,t1=caps('OPEN AUTONOMOUS'); d2,t2=caps('SYSTEMS ALLIANCE'); ts=ww*0.70/max(t1,t2); ty=wy+wh+22; lh=700*ts*1.55
    body=(mark(mx,my,m,mv)+wordmark(wx,wy,wh,ink)+
          f'<path transform="translate({wx+4:.1f} {ty:.1f}) scale({ts:.5f})" fill="{sub}" d="{d1}"/>'
          f'<path transform="translate({wx+4:.1f} {ty+lh:.1f}) scale({ts:.5f})" fill="{sub}" d="{d2}"/>')
    return wx+ww+20, max(10+art_h+10, ty+lh+700*ts+10), title, body
def appicon(title, bg, mv):
    s=1024; m=s*0.86; mx=(s-m)/2; my=(s-m*(330+40)/512)/2 - m*40/512+s*0.005
    return s, s, title, f'<rect width="{s}" height="{s}" rx="{s*0.2237:.0f}" fill="{bg}"/>'+mark(mx,my,m,mv)

files={
 'oasa-logo-vertical':          (vertical,   ('OASA, Open Autonomous Systems Alliance','oasa-mark',NAVY,NAVY)),
 'oasa-logo-vertical-on-dark':  (vertical,   ('OASA, Open Autonomous Systems Alliance','oasa-mark-on-dark',WHITE,WHITE)),
 'oasa-logo-horizontal':        (horizontal, ('OASA, Open Autonomous Systems Alliance','oasa-mark',NAVY,NAVY)),
 'oasa-logo-horizontal-on-dark':(horizontal, ('OASA, Open Autonomous Systems Alliance','oasa-mark-on-dark',WHITE,WHITE)),
 'oasa-logo-horizontal-navy':   (horizontal, ('OASA, Open Autonomous Systems Alliance','oasa-mark-navy',NAVY,NAVY)),
 'oasa-logo-horizontal-white':  (horizontal, ('OASA, Open Autonomous Systems Alliance','oasa-mark-white',WHITE,WHITE)),
 'oasa-logo-horizontal-black':  (horizontal, ('OASA, Open Autonomous Systems Alliance','oasa-mark-black',BLACK,BLACK)),
 'oasa-app-icon':               (appicon,    ('OASA app icon',NAVY,'oasa-mark-on-dark')),
}
for name,(fn,args) in files.items():
    w,h,title,body=fn(*args); open(f'{OUT}/{name}.svg','w').write(doc(w,h,title,body))
for v in ['oasa-mark','oasa-mark-on-dark','oasa-mark-navy','oasa-mark-white','oasa-mark-black']:
    open(f'{OUT}/{v}.svg','w').write(open(f'{S}/{v}.svg').read())
for v,ink in [('oasa-wordmark',NAVY),('oasa-wordmark-white',WHITE)]:
    open(f'{OUT}/{v}.svg','w').write(doc(WW+40,WH+40,'OASA',wordmark(20,30,730,ink)))
print('wrote', len(files)+7, 'files')

# Square crops of the mark (art spans x 39..473, y 40..330): favicons, small spots.
for v in ['oasa-mark','oasa-mark-on-dark']:
    s=open(f'{S}/{v}.svg').read().replace('viewBox="0 0 512 512"','viewBox="30 -38 452 452"',1)
    open(f'{OUT}/{v}-square.svg','w').write(s)
# Avatar: full-bleed navy square, mark centered inside the circle crop.
m=0.80*1024; mx=(1024-m)/2; my=(1024-m*(330+40)/512)/2-m*40/512
open(f'{OUT}/oasa-avatar.svg','w').write(doc(1024,1024,'OASA avatar',f'<rect width="1024" height="1024" fill="{NAVY}"/>'+mark(mx,my,m,'oasa-mark-on-dark')))
