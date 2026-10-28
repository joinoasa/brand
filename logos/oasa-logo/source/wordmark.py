from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
S='.'  # folder holding the generated SVGs and the Sora .ttf instances
f=TTFont(f'{S}/sora800.ttf'); gs=f.getGlyphSet(); cmap=f.getBestCmap(); hm=f['hmtx']
LAMBDA=[(8,0),(318,730),(464,730),(782,0),(590,0),(391,548),(194,0)]
TRACK=10
EMBOLDEN=34  # extra weight beyond Sora 800, matches the concept
def word(fill='#0B253A'):
    """Return (svg path d, width, height) for OASA, y-down, baseline at 730."""
    x=0; ds=[]
    for ch in 'OASA':
        if ch=='A':
            pts=' '.join(f'{x+px:.1f} {730-py:.1f}' for px,py in LAMBDA)
            ds.append('M'+pts.replace(' ',',',0)+' Z'); adv=788
            ds[-1]='M'+' L'.join(f'{x+px:.1f} {730-py:.1f}' for px,py in LAMBDA)+' Z'
        else:
            g=cmap[ord(ch)]; pen=SVGPathPen(gs); gs[g].draw(TransformPen(pen,(1,0,0,-1,x,730))); ds.append(pen.getCommands()); adv=hm[g][0]
        x+=adv+TRACK
    return ' '.join(ds), x-TRACK, 752+20
if __name__=='__main__':
    d,w,h=word()
    open(f'{S}/oasa-wordmark.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -40 {w+40:.0f} {h+40:.0f}" role="img" aria-label="OASA"><path fill="#0B253A" stroke="#0B253A" stroke-width="{EMBOLDEN}" stroke-linejoin="miter" stroke-miterlimit="4" d="{d}"/></svg>\n')
    print(w,h)
