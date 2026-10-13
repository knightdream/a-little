from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
S=2; W=640; H=490; FLOOR=432
parts={f.stem:Image.open(f).convert('RGBA') for f in (P.parent/'黑发A行走修正版'/'部件').glob('*.png')}
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

# Key poses: frame, hip shift, lean, upper-arm angle, forearm angle, wrench angle.
KEYS=[
 (0,0,.08,.12,.57,.3),
 (5,-8,-.06,-1.7,-2.8,2.4),
 (8,-10,-.10,-2.1,-3.0,2.9),
 (10,7,.15,-.35,-4.3,4.0),
 (12,20,.30,1.3,1.65,4.8),
 (15,23,.34,.65,1.0,6.35),
 (18,14,.22,.25,.7,6.65),
 (23,0,.08,.12,.57,6.583185307179586)]
def pose(n):
 for a,b in zip(KEYS,KEYS[1:]):
  if a[0]<=n<=b[0]:
   u=(n-a[0])/(b[0]-a[0]);u=u*u*(3-2*u)
   return [x+(y-x)*u for x,y in zip(a[1:],b[1:])]
 raise ValueError(n)

def render(n):
 canvas=Image.new('RGBA',(W*S,H*S))
 shift,lean,upper,fore,weapon=pose(n)
 # Arm angles are unwrapped along the shortest intended overhead path.
 if 8<n<12:
  # Wrist arc passes over the head before the arm extends forward.
  u=(n-8)/4
  upper=-2.1+3.4*u
  fore=-3.0-1.633185307179586*u
 hip=(300+shift,280+abs(shift)*.16)
 def bp(x,y):return (hip[0]+x*math.cos(lean)-y*math.sin(lean),hip[1]+x*math.sin(lean)+y*math.cos(lean))
 neck=bp(5,-97)
 def leg(side):
  ankle=(320 if side=='near' else 273,FLOOR-31);knee=ik(hip,ankle)
  segment(canvas,'calf_'+side,knee,ankle,(82,29),(82,205))
  im=parts['boot_'+side];paste_affine(canvas,im,(82,16),ankle,31/(im.height-16))
  segment(canvas,'thigh_'+side,hip,knee,(60,31),(77,297))
 def arm(side):
  sh=bp(-30 if side=='near' else 8,-73)
  th=upper if side=='near' else -.2-shift*.022
  ft=fore if side=='near' else th+.65
  el=(sh[0]+45*math.sin(th),sh[1]+45*math.cos(th))
  wr=(el[0]+42*math.sin(ft),el[1]+42*math.cos(ft))
  if side=='near':paste_affine(canvas,parts['wrench'],(64,44),(wr[0]-3,wr[1]+5),.37,weapon%(2*math.pi))
  segment(canvas,'forearm_'+side,el,wr,(47,27),(47,228))
  segment(canvas,'arm_'+side,sh,el,(76,27),(56,223))
 leg('far');arm('far');leg('near')
 paste_affine(canvas,parts['pelvis'],(103,70),(hip[0]+1,hip[1]-4),.34,lean*.4)
 paste_affine(canvas,parts['torso'],(159,53),neck,.44,lean)
 paste_affine(canvas,parts['head'],(156,225),(neck[0]-2,neck[1]+3),.44,lean*.25)
 arm('near')
 return canvas.resize((W,H),Image.Resampling.LANCZOS)

out=P/'attack';out.mkdir(exist_ok=True)
frames=[];previews=[]
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
for n in range(24):
 im=render(n);im.save(out/f'{n:02d}.png');frames.append(im)
 assert im.getbbox()[0]>0 and im.getbbox()[1]>0 and im.getbbox()[2]<W and im.getbbox()[3]<H, ('clipping',n,im.getbbox())
 bg=Image.new('RGB',(W,H),(18,25,40));d=ImageDraw.Draw(bg)
 d.text((20,16),'ATTACK / A / 24 FRAMES',font=font,fill=(242,212,130))
 d.line((12,FLOOR+1,W-12,FLOOR+1),fill=(65,85,103),width=2)
 bg.paste(im,(0,0),im)
 stage='WINDUP' if n<9 else ('SWING' if n<16 else 'RECOVER')
 d.text((20,463),f'{n+1:02d} / 24  |  '+stage,font=font,fill=(171,184,201));previews.append(bg)
assert np.max(np.abs(np.asarray(frames[0]).astype(int)-np.asarray(frames[-1]).astype(int)))<=1
previews[0].save(P/'攻击.gif',save_all=True,append_images=previews[1:],duration=[40]*9+[30]*7+[45]*7+[300],loop=0,optimize=False)
previews[0].save(P/'攻击慢放.gif',save_all=True,append_images=previews[1:],duration=120,loop=0,optimize=False)
sheet=Image.new('RGBA',(W*6,H*4))
for n,f in enumerate(frames):sheet.alpha_composite(f,((n%6)*W,(n//6)*H))
sheet.save(P/'attack-24.png')
contact=Image.new('RGB',(W*4,H*2))
for k,n in enumerate([0,5,8,10,12,15,18,23]):contact.paste(previews[n],((k%4)*W,(k//4)*H))
contact.save(P/'关键姿势.png')
print('24 attack frames exported; no clipping; first/last pose match.')
