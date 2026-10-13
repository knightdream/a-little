from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
S=2; W=440; H=490; FLOOR=432
parts={f.stem:Image.open(f).convert('RGBA') for f in (P/'部件').glob('*.png')}
parts['torso']=parts['torso'].crop((0,0,parts['torso'].width,220))
# Separate ankle boots from calf cloth so planted soles remain horizontal.
for side in ['near','far']:
 im=parts['shin_'+side]
 parts['calf_'+side]=im.crop((0,0,im.width,221))
 parts['boot_'+side]=im.crop((0,201,im.width,im.height))

def paste_affine(dst,img,anchor,dest,scale=1,angle=0):
 # forward: dest + scale * R * (source - anchor), converted to PIL inverse map
 c=math.cos(angle);s=math.sin(angle);q=scale*S
 a=c/q;b=s/q;d=-s/q;e=c/q
 x,y=dest[0]*S,dest[1]*S
 coeff=(a,b,anchor[0]-a*x-b*y,d,e,anchor[1]-d*x-e*y)
 layer=img.transform(dst.size,Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC)
 dst.alpha_composite(layer)

def segment(dst,name,a,b,p0,p1):
 dx=b[0]-a[0];dy=b[1]-a[1];sx=p1[0]-p0[0];sy=p1[1]-p0[1]
 scale=math.hypot(dx,dy)/math.hypot(sx,sy)
 angle=math.atan2(dy,dx)-math.atan2(sy,sx)
 paste_affine(dst,parts[name],p0,a,scale,angle)

def ik(hip,ankle,l1=75,l2=69):
 dx=ankle[0]-hip[0];dy=ankle[1]-hip[1];r=math.hypot(dx,dy)
 if r>=l1+l2: raise ValueError(('leg beyond reach',r))
 a=(l1*l1-l2*l2+r*r)/(2*r);h=math.sqrt(max(0,l1*l1-a*a))
 return (hip[0]+dx*a/r+dy*h/r,hip[1]+dy*a/r-dx*h/r)

def foot(t):
 u=t%1;stride=86
 if u<.60:return (stride/2-stride*u/.60,FLOOR-31,True)
 v=(u-.60)/.40
 return (-stride/2+stride*(v*v*(3-2*v)),FLOOR-31-25*math.sin(math.pi*v),False)

def render(t,debug=False):
 canvas=Image.new('RGBA',(W*S,H*S))
 bob=2.3*math.cos(4*math.pi*t)
 hip=(220,269+bob);neck=(225,172+bob)
 joints={};armdata={}
 for side,offset in [('near',0),('far',.5)]:
  dx,ay,stance=foot(t+offset);ankle=(hip[0]+dx,ay)
  knee=ik(hip,ankle)
  joints[side]=(hip,knee,ankle,stance)
  # ipsilateral hand travels opposite the ipsilateral foot.
  phase=2*math.pi*(t+offset)
  theta=-(.46 if side=='near' else .65)*math.cos(phase)
  shoulder=(190 if side=='near' else 228,196+bob)
  elbow=(shoulder[0]+45*math.sin(theta),shoulder[1]+45*math.cos(theta))
  foretheta=theta+.13
  wrist=(elbow[0]+42*math.sin(foretheta),elbow[1]+42*math.cos(foretheta))
  armdata[side]=(shoulder,elbow,wrist,theta)
 def leg(side):
  h,k,a,_=joints[side]
  # Lower layer first, then thigh masks knee art and joint seam.
  segment(canvas,'calf_'+side,k,a,(82,29),(82,205))
  im=parts['boot_'+side];paste_affine(canvas,im,(82,16),a,31/(im.height-16))
  segment(canvas,'thigh_'+side,h,k,(60,31),(77,297))
 def arm(side):
  sh,el,wr,theta=armdata[side]
  if side=='near':
   # Weapon follows hand, using limited angular motion for its weight.
   paste_affine(canvas,parts['wrench'],(64,44),(wr[0]-3,wr[1]+5),.37,-theta*.28+.17)
  segment(canvas,'forearm_'+side,el,wr,(47,27),(47,228))
  segment(canvas,'arm_'+side,sh,el,(76,27),(56,223))
 leg('far');arm('far');leg('near')
 paste_affine(canvas,parts['pelvis'],(103,70),(hip[0]+1,hip[1]-4),.34)
 paste_affine(canvas,parts['torso'],(159,53),neck,.44)
 arm('near')
 # A tiny counterrotation keeps the head stable instead of a rigid whole-body tilt.
 paste_affine(canvas,parts['head'],(156,225),(neck[0]-2,neck[1]+3),.44,.012*math.sin(2*math.pi*t))
 if debug:
  d=ImageDraw.Draw(canvas)
  for side,color in [('near',(80,223,245,255)),('far',(255,135,100,255))]:
   h,k,a,st=joints[side];sh,el,wr,th=armdata[side]
   for chain in [(h,k,a),(sh,el,wr)]:
    pts=[(int(x*S),int(y*S)) for x,y in chain];d.line(pts,fill=color,width=3*S)
    for x,y in pts:d.ellipse((x-4*S,y-4*S,x+4*S,y+4*S),fill=color)
 return canvas.resize((W,H),Image.Resampling.LANCZOS),joints,armdata

out=P/'walk';out.mkdir(exist_ok=True)
frames=[];trace=[]
for n in range(24):
 im,j,a=render(n/24);im.save(out/f'{n:02d}.png');frames.append(im)
 trace.append({'frame':n+1,'nearFoot':list(j['near'][2]),'farFoot':list(j['far'][2]),'nearStance':j['near'][3],'farStance':j['far'][3],'nearHand':list(a['near'][2]),'farHand':list(a['far'][2])})
# Check continuous-loop math, foot alternation, arm/leg opposition, and fixed soles.
f0,_,_=render(0);f1,_,_=render(1);assert np.array_equal(np.array(f0),np.array(f1))
for side in ['near','far']:
 footx=np.array([r[side+'Foot'][0] for r in trace]);handx=np.array([r[side+'Hand'][0] for r in trace])
 assert np.corrcoef(footx,handx)[0,1]<-.7
 for r in trace:
  if r[side+'Stance']:assert abs(r[side+'Foot'][1]+31-FLOOR)<.001
assert np.corrcoef([r['nearFoot'][0] for r in trace],[r['farFoot'][0] for r in trace])[0,1]<-.85
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
previews=[];diagnostics=[]
for n,f in enumerate(frames):
 bg=Image.new('RGB',(W,H),(18,25,40));d=ImageDraw.Draw(bg)
 d.text((20,15),'WALK / A / 24 FRAMES',font=font,fill=(242,212,130))
 d.line((12,FLOOR+1,W-12,FLOOR+1),fill=(65,85,103),width=2)
 bg.paste(f,(0,0),f);d.text((20,463),f'{n+1:02d} / 24  |  20 fps',font=small,fill=(171,184,201))
 previews.append(bg)
 debug=render(n/24,True)[0];diag=Image.new('RGB',(W,H),(18,25,40));diag.paste(debug,(0,0),debug);diagnostics.append(diag)
previews[0].save(P/'行走修正版.gif',save_all=True,append_images=previews[1:],duration=50,loop=0,optimize=False)
previews[0].save(P/'行走慢放.gif',save_all=True,append_images=previews[1:],duration=120,loop=0,optimize=False)
diagnostics[0].save(P/'步态检查.gif',save_all=True,append_images=diagnostics[1:],duration=120,loop=0,optimize=False)
sheet=Image.new('RGBA',(W*6,H*4))
for n,f in enumerate(frames):sheet.alpha_composite(f,((n%6)*W,(n//6)*H))
sheet.save(P/'walk-24.png')
contact=Image.new('RGB',(W*4,H*2))
for k,n in enumerate(range(0,24,3)):contact.paste(previews[n],((k%4)*W,(k//4)*H))
contact.save(P/'八个关键姿势.png')
(P/'步态数据.json').write_text(json.dumps(trace,indent=2))
print('24 unique frames; exact periodic loop, alternating legs, opposite arm swing and planted-foot height checks passed.')
