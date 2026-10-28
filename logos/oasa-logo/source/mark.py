import sys
S='.'  # folder holding the generated SVGs and the Sora .ttf instances
C=425; k=0.63
def P(x,y): return (round(256+(x-C)*k,1), round(40+(y-68)*k,1))
w=345; ty=535
def circ(apex):
    h=ty-apex; R=(w*w+h*h)/(2*h); return (apex+R, R)
up=circ(388); lo=circ(450); gap=17
cx=256.0; cy=P(C,up[0])[1]; Ru=round(up[1]*k,1); cyl=P(C,lo[0])[1]; Rl=round(lo[1]*k,1); Rcut=round((up[1]+gap)*k,1)
L=[P(138,492),P(330,208),P(378,221),P(404,300),P(350,448)]
R=[(round(512-x,1),y) for (x,y) in L]
pts=lambda a:' '.join(f'{x},{y}' for x,y in a)
sx,sy=P(C,166); v=round(100*k,1); h=round(86*k,1); c=round(7*k,1)
st=(f"M{sx} {round(sy-v,1)} Q{round(sx+c,1)} {round(sy-c,1)} {round(sx+h,1)} {sy} "
    f"Q{round(sx+c,1)} {round(sy+c,1)} {sx} {round(sy+v,1)} Q{round(sx-c,1)} {round(sy+c,1)} {round(sx-h,1)} {sy} "
    f"Q{round(sx-c,1)} {round(sy-c,1)} {sx} {round(sy-v,1)} Z")
def svg(title, peak, star, horizon_fill, defs_extra=''):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-labelledby="t">
  <title id="t">{title}</title>
  <defs>{defs_extra}
    <clipPath id="in-upper"><circle cx="{cx}" cy="{cy}" r="{Ru}"/></clipPath>
    <mask id="cut" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512">
      <rect width="512" height="512" fill="#fff"/>
      <circle cx="{cx}" cy="{cy}" r="{Rcut}" fill="#000"/>
      <path d="{st}" fill="#000" stroke="#000" stroke-width="24" stroke-linejoin="round"/>
    </mask>
  </defs>
  <!-- split peak -->
  <g fill="{peak}" mask="url(#cut)">
    <polygon points="{pts(L)}"/>
    <polygon points="{pts(R)}"/>
  </g>
  <!-- horizon: inside the upper circle, outside the lower one -->
  <g clip-path="url(#in-upper)"><path fill="{horizon_fill}" fill-rule="evenodd" d="M-1 -1 H513 V513 H-1 Z M{cx} {round(cyl-Rl,1)} A{Rl} {Rl} 0 1 0 {cx+0.01} {round(cyl-Rl,1)} Z"/></g>
  <!-- guiding star -->
  <path d="{st}" fill="{star}"/>
</svg>
'''
grad=lambda a,b,i: f'''
    <linearGradient id="{i}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'''
variants={
 'oasa-mark':            svg('OASA mark','#0B253A','#E3A32C','url(#hz)',grad('#1F6FA3','#2BA6A6','hz')),
 'oasa-mark-on-dark':    svg('OASA mark (on dark)','#FFFFFF','#E3A32C','url(#hz)',grad('#2B9FD0','#3CC6C4','hz')),
 'oasa-mark-navy':       svg('OASA mark (one color, navy)','#0B253A','#0B253A','#0B253A'),
 'oasa-mark-white':      svg('OASA mark (one color, white)','#FFFFFF','#FFFFFF','#FFFFFF'),
 'oasa-mark-black':      svg('OASA mark (one color, black)','#000000','#000000','#000000'),
}
for n,s in variants.items(): open(f'{S}/{n}.svg','w').write(s)
print('ok')
