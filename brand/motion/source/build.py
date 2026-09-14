"""Build approved-path motion SVGs, gallery and portable video/GIF previews.
Requires rsvg-convert, Pillow and imageio-ffmpeg. Run from any directory.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json, subprocess, io, hashlib, shutil
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];BRAND=ROOT.parent
NS={'s':'http://www.w3.org/2000/svg'}
paths={p.attrib['id'].split('-')[-1]:p.attrib['d'] for p in ET.parse(BRAND/'viable-soft-wordmark.svg').findall('.//s:path',NS)}
DURATION=10;FPS=15;W,H=960,300
# Each track contains [fraction, x offset, y offset, opacity].
def track(points):return points
def basic():return {c:[[0,0,0,1],[1,0,0,1]] for c in 'VIABLE'}
def short(c):return {'V':136,'B':-32,'L':-44}.get(c,0)
def make_tracks(style):
 t=basic()
 if style in [1,4]:
  for c in 'VBL':t[c]=[[0,0,0,1],[.26,0,0,1],[.44,short(c),0,1],[.60,short(c),0,1],[.82,0,0,1],[1,0,0,1]]
  for i,c in enumerate('IAE'):
   a=.18+(i*.035 if style==4 else 0);b=a+.14;y=-24 if style==4 else 0
   t[c]=[[0,0,0,1],[a,0,0,1],[b,0,y,0],[1-b,0,y,0],[1-a,0,0,1],[1,0,0,1]]
 elif style==5:
  t['V']=[[0,0,0,1],[.12,0,0,1],[.28,224,0,1],[.36,224,0,1],[.5,136,0,1],[.62,136,0,1],[.76,224,0,1],[.82,224,0,1],[1,0,0,1]]
  for c in 'BL':t[c]=[[0,0,0,1],[.12,0,0,1],[.24,0,0,0],[.36,short(c),12,0],[.5,short(c),0,1],[.62,short(c),0,1],[.74,short(c),12,0],[.86,0,0,0],[1,0,0,1]]
  for c in 'IAE':t[c]=[[0,0,0,1],[.12,0,0,1],[.24,0,0,0],[.86,0,0,0],[1,0,0,1]]
 return t
STYLES=[('01-signature','Signature','The current website signature: letters settle into VBL, then return.'),('02-soft-crossfade','Soft dissolve','The full wordmark fades out before the short form settles into place.'),('03-reveal','Reveal','A horizontal wipe reveals the short form and returns to VIABLE.'),('04-stagger','Stagger','I, A and E lift away in sequence while V, B and L come together.'),('05-v-bridge','V bridge','VIABLE becomes V, then VBL, then V, and returns to VIABLE.')]
def path(c,fill='#003153'):return f'<path data-letter="{c}" fill="{fill}" d="{paths[c]}"/>'
def svg(style,static=None,white=False):
 key=STYLES[style-1][0];prefix='m'+str(style);fill='#ffffff' if white else '#003153';styles=[];body=''
 if style in [1,4,5]:
  for c,points in make_tracks(style).items():
   if static is None:
    frames=''.join(f'{f*100:g}%{{transform:translate({x:g}px,{y:g}px);opacity:{o:g}}}' for f,x,y,o in points)
    styles.append(f'@keyframes {prefix}{c}{{{frames}}}.{prefix}{c}{{animation:{prefix}{c} 10s ease-in-out infinite;transform-origin:0 0}}')
    body+=f'<g class="motion-part {prefix}{c}">'+path(c,fill)+'</g>'
   else:
    x,y,o=sample(points,static);body+=f'<g transform="translate({x} {y})" opacity="{o}">'+path(c,fill)+'</g>'
 else:
  if style==2:
   full=[[0,0,0,1],[.18,0,0,1],[.28,0,-12,0],[.72,0,-12,0],[.82,0,0,1],[1,0,0,1]]
   compact=[[0,0,12,0],[.28,0,12,0],[.38,0,0,1],[.62,0,0,1],[.72,0,12,0],[1,0,12,0]]
   for label,points,letters in [('full',full,'VIABLE'),('short',compact,'VBL')]:
    shape=''.join(f'<g transform="translate({short(c) if label=="short" else 0} 0)">{path(c,fill)}</g>' for c in letters)
    if static is None:
     frames=''.join(f'{f*100:g}%{{transform:translate({x:g}px,{y:g}px);opacity:{o:g}}}' for f,x,y,o in points)
     styles.append(f'@keyframes {prefix}{label}{{{frames}}}.{prefix}{label}{{animation:{prefix}{label} 10s ease-in-out infinite}}')
     body+=f'<g class="motion-part {prefix}{label}" style="opacity:{1 if label=="full" else 0}">{shape}</g>'
    else:
     x,y,o=sample(points,static);body+=f'<g transform="translate({x} {y})" opacity="{o}">{shape}</g>'
  else:
   full=[[0,0,0,1],[.18,0,0,1],[.28,1,0,1],[.72,1,0,1],[.82,0,0,1],[1,0,0,1]]
   compact=[[0,0,0,1],[.28,0,0,1],[.38,1,0,1],[.62,1,0,1],[.72,0,0,1],[1,0,0,1]]
   body='<defs>'
   for label,points,start in [('f',full,30),('s',compact,-530)]:
    if static is None:
     frames=''.join(f'{f*100:g}%{{transform:translateX({560*x:g}px)}}' for f,x,y,o in points)
     styles.append(f'@keyframes {prefix}{label}clip{{{frames}}}.{prefix}{label}clip{{animation:{prefix}{label}clip 10s ease-in-out infinite}}')
     attr=f'class="motion-part {prefix}{label}clip"'
    else:attr=f'transform="translate({560*sample(points,static)[0]} 0)"'
    body+=f'<clipPath id="{prefix}{label}"><rect {attr} x="{start}" y="0" width="560" height="180"/></clipPath>'
   body+='</defs>'
   body+=f'<g clip-path="url(#{prefix}f)">'+''.join(path(c,fill) for c in 'VIABLE')+'</g>'
   body+=f'<g clip-path="url(#{prefix}s)">'+''.join(f'<g transform="translate({short(c)} 0)">{path(c,fill)}</g>' for c in 'VBL')+'</g>'
 styles.append('@media(prefers-reduced-motion:reduce){.motion-part{animation:none!important}}')
 title=STYLES[style-1][1]
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -10 620 194" width="960" height="300" role="img" aria-labelledby="{prefix}title"><title id="{prefix}title">VIABLE to VBL and back: {title}</title><desc>Approved Soft artwork. Ten-second loop. Reduced motion shows VIABLE.</desc><style>{"".join(styles)}</style>{body}</svg>'
def sample(points,f):
 for i in range(len(points)-1):
  a,b=points[i:i+2]
  if a[0]<=f<=b[0]:
   u=(f-a[0])/(b[0]-a[0]);u=u*u*(3-2*u)
   return [a[k]+(b[k]-a[k])*u for k in [1,2,3]]
 return points[-1][1:]
def png(data):
 b=subprocess.check_output(['rsvg-convert','-w',str(W),'-h',str(H)],input=data.encode());im=Image.open(io.BytesIO(b)).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);return bg.convert('RGB')
def build_preview(style):
 key=STYLES[style-1][0];frames=[]
 for frame in range(DURATION*FPS):frames.append(png(svg(style,frame/(DURATION*FPS))))
 ff=imageio_ffmpeg.get_ffmpeg_exe();p=subprocess.Popen([ff,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/(key+'.mp4'))],stdin=subprocess.PIPE)
 for im in frames:p.stdin.write(im.tobytes())
 p.stdin.close();assert p.wait()==0
 frames[0].save(ROOT/(key+'-poster.png'))
 gif=[im.resize((640,200)).quantize(colors=64) for im in frames]
 gif[0].save(ROOT/(key+'.gif'),save_all=True,append_images=gif[1:],duration=[(round((i+1)*100/FPS)-round(i*100/FPS))*10 for i in range(len(gif))],loop=0,optimize=True,disposal=2)
 print('Rendered',key,flush=True)
for i,(key,title,desc) in enumerate(STYLES,1):
 (ROOT/(key+'.svg')).write_text(svg(i));(ROOT/(key+'-white.svg')).write_text(svg(i,white=True))
with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(build_preview,range(1,6)))
# Separate static symbols and short wordmarks use exact approved paths.
icons=BRAND/'icons';icons.mkdir(exist_ok=True)
for suffix in ['','-white']:
 for ext in ['svg','png']:shutil.copyfile(BRAND/f'viable-soft-symbol{suffix}.{ext}',icons/f'VIABLE-V{suffix}.{ext}')
 for label,letters,view in [('VBL','VBL','150 20 320 133'),('VIABLE','VIABLE','20 20 580 133')]:
  body=''.join(f'<g transform="translate({short(c) if label=="VBL" else 0} 0)">{path(c,"#fff" if suffix else "#003153")}</g>' for c in letters)
  data=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}" role="img" aria-label="{label}">{body}</svg>'
  (icons/f'{label}{suffix}.svg').write_text(data)
  subprocess.run(['rsvg-convert','-w','1200','-o',str(icons/f'{label}{suffix}.png')],input=data.encode(),check=True)
# Inline SVG gallery provides pause, replay, reduced-motion and offscreen controls.
cards=[]
for i,(key,title,desc) in enumerate(STYLES,1):cards.append(f'<article><div class="stage" data-motion>{svg(i)}</div><div class="card-copy"><small>0{i} / 10 SECONDS</small><h2>{title}</h2><p>{desc}</p><button data-toggle aria-pressed="false">Pause</button> <button data-replay>Replay</button><p class="downloads"><a href="{key}.svg" download>SVG</a> · <a href="{key}-white.svg" download>White SVG</a> · <a href="{key}.mp4" download>MP4</a> · <a href="{key}.gif" download>GIF</a></p></div></article>')
html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>VIABLE · Motion library</title><style>
*{box-sizing:border-box}body{margin:0;background:#fff;color:#003153;font:16px/1.6 system-ui,sans-serif}main{max-width:1160px;margin:auto;padding:48px 24px}h1{font-size:clamp(32px,5vw,48px);line-height:1.15;letter-spacing:-.04em;margin:22px 0 16px}header p{max-width:660px;color:#5a6b7a}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:36px 0}article{border:1px solid #dbe4e9;border-radius:12px;overflow:hidden}.stage{padding:36px 20px;background:#f8fafb;border-bottom:1px solid #dbe4e9}.stage svg{display:block;width:100%;height:auto}.card-copy{padding:24px}.card-copy p{color:#5a6b7a}h2{font-size:23px;line-height:1.2}small{font-size:11px;letter-spacing:.12em}a{color:inherit}button{font:inherit;color:#003153;background:white;border:1px solid #cad9e2;border-radius:6px;min-height:44px;padding:7px 16px;cursor:pointer}button:focus-visible,a:focus-visible{outline:2px solid #003153;outline-offset:4px}.stage.paused .motion-part{animation-play-state:paused!important}.icons{display:flex;gap:24px;align-items:center;margin:20px 0}.icons img{width:88px;height:88px}.downloads{font-size:14px}footer{border-top:1px solid #dbe4e9;padding-top:20px;font-size:14px;color:#5a6b7a}@media(max-width:720px){.grid{grid-template-columns:1fr}main{padding:30px 20px}}
</style></head><body><main><header><img src="../viable-soft-wordmark.svg" alt="VIABLE" width="156" height="32"><h1>One identity. Five ways to move.</h1><p>VIABLE to VBL and back. Exact Soft artwork, Berlin blue and quiet motion. Choose a variant; download only what you need.</p><a href="../VIABLE-Motion-and-V-Kit.zip" download>Download the complete kit →</a></header><div class="grid">'''+''.join(cards)+'''</div><section><h2>The standalone V</h2><div class="icons"><img src="../icons/VIABLE-V.svg" alt="Standalone V icon"><div><a href="../icons/VIABLE-V.svg" download>Blue SVG</a> · <a href="../icons/VIABLE-V.png" download>Blue PNG</a><br><a href="../icons/VIABLE-V-white.svg" download>White SVG</a> · <a href="../icons/VIABLE-V-white.png" download>White PNG</a></div></div><p>Use V for icons and compact placements. VIABLE is the complete wordmark; do not add an extra V before it.</p></section><footer>Ten-second loops. Use one animation at a time in customer-facing pages. This gallery pauses offscreen and respects reduced motion. SVG is the lightweight web master; MP4 and GIF are portable previews.</footer></main><script>
const reduce=matchMedia('(prefers-reduced-motion: reduce)');document.querySelectorAll('article').forEach(card=>{const stage=card.querySelector('.stage'),toggle=card.querySelector('[data-toggle]');let userPaused=false,visible=false;function sync(){stage.classList.toggle('paused',userPaused||!visible||document.hidden||reduce.matches);toggle.disabled=reduce.matches;toggle.textContent=reduce.matches?'Reduced motion':userPaused?'Play':'Pause';toggle.setAttribute('aria-pressed',String(userPaused));}toggle.onclick=()=>{userPaused=!userPaused;sync()};card.querySelector('[data-replay]').onclick=()=>{stage.getAnimations({subtree:true}).forEach(a=>a.currentTime=0);userPaused=false;sync()};new IntersectionObserver(es=>{visible=es[0].isIntersecting;sync()}).observe(stage);document.addEventListener('visibilitychange',sync);reduce.addEventListener('change',sync);sync()});
</script></body></html>'''
(ROOT/'index.html').write_text(html)
(ROOT/'README.md').write_text('''# VIABLE motion library

Five distinct 10-second loops, each travelling VIABLE → VBL → VIABLE. V bridge also passes through the standalone V. 01 Signature reproduces the current website choreography. All letters use the exact approved Soft paths; no extra V is attached to VIABLE.

- SVG / white SVG: lightweight vector web masters, transparent background, reduced-motion fallback.
- MP4: 960×300, 15 fps, white background, one complete loop. Set loop in the player if needed.
- GIF: 640×200, white background, looping preview. GIF is not the preferred web format and cannot obey reduced-motion settings on its own.
- index.html: gallery with pause/replay and offscreen/hidden-tab pausing. Open via a local HTTP server or the hosted gallery.
- ../icons: standalone V, VBL and VIABLE, blue/white SVG and transparent PNG.
- source/build.py: reproducible generator; requires rsvg-convert, Pillow, imageio-ffmpeg.

Use only one moving logo on a customer page. Keep the existing homepage animation unless a replacement is deliberately selected. VIABLE is the full company name; VBL is the short form. V is a separate icon for favicons, avatars, app icons and limited-space placements.

SVG uses browser ease-in-out interpolation; raster previews approximate easing with smoothstep. Artwork, states and timing are the same. Reduced motion leaves a static VIABLE wordmark. Static PNG/SVG alternatives are included.
''')
manifest={'name':'VIABLE Motion and V Kit','version':'2026-09-14','color':'#003153','duration_seconds':10,'variants':[{'id':key,'name':title,'direction':'VIABLE → VBL → VIABLE','description':desc} for key,title,desc in STYLES],'files':{}}
for p in list(ROOT.rglob('*'))+list(icons.glob('*')):
 if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts:manifest['files'][str(p.relative_to(BRAND))]=hashlib.sha256(p.read_bytes()).hexdigest()
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Built motion library',ROOT)
