from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
S=2; W=440; H=490; FLOOR=432
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

def render(t,debug=False):
 canvas=Image.new('RGBA',(W*S,H*S))
 n=t
 flight=4<=n<=19
 u=max(0,min(1,(n-4)/15))
 tuck=math.sin(math.pi*u) if flight else 0
 if n<4: crouch=14*math.sin(math.pi*n/6)
 elif n>19: crouch=16*math.sin(math.pi*(n-19)/4)
 else: crouch=0
 hip=(210,280+crouch);lean=.08+.10*tuck+.006*crouch
 def bodypoint(x,y):
  return (hip[0]+x*math.cos(lean)-y*math.sin(lean),hip[1]+x*math.sin(lean)+y*math.cos(lean))
 neck=bodypoint(5,-97)
 joints={};armdata={}
 for side,offset in [('near',0),('far',.5)]:
  stance=not flight or n in (4,19)
  dx=(16 if side=='near' else -19)+(9 if side=='near' else -8)*tuck
  ay=FLOOR-31-(48 if side=='near' else 30)*tuck
  ankle=(hip[0]+dx,ay)
  knee=ik(hip,ankle)
  joints[side]=(hip,knee,ankle,stance)
  # ipsilateral hand travels opposite the ipsilateral foot.
  phase=2*math.pi*(t+offset)
  theta=(.12 if side=='near' else -.15)+(.65 if side=='near' else .9)*tuck-.018*crouch
  shoulder=bodypoint(-30 if side=='near' else 8,-73)
  elbow=(shoulder[0]+45*math.sin(theta),shoulder[1]+45*math.cos(theta))
  foretheta=theta+.45+.55*tuck
  wrist=(elbow[0]+42*math.sin(foretheta),elbow[1]+42*math.cos(foretheta))
  armdata[side]=(shoulder,elbow,wrist,theta)
 def leg(side):
  h,k,a,stance=joints[side]
  # Lower layer first, then thigh masks knee art and joint seam.
  segment(canvas,'calf_'+side,k,a,(82,29),(82,205))
  im=parts['boot_'+side]
  toe=0 if stance else -.22*tuck
  paste_affine(canvas,im,(82,16),a,31/(im.height-16),toe)
  segment(canvas,'thigh_'+side,h,k,(60,31),(77,297))
 def arm(side):
  sh,el,wr,theta=armdata[side]
  if side=='near':
   # Weapon follows hand, using limited angular motion for its weight.
   paste_affine(canvas,parts['wrench'],(64,44),(wr[0]-3,wr[1]+5),.37,-theta*.35+.35)
  segment(canvas,'forearm_'+side,el,wr,(47,27),(47,228))
  segment(canvas,'arm_'+side,sh,el,(76,27),(56,223))
 leg('far');arm('far');leg('near')
 paste_affine(canvas,parts['pelvis'],(103,70),(hip[0]+1,hip[1]-4),.34,lean*.4)
 paste_affine(canvas,parts['torso'],(159,53),neck,.44,lean)
 arm('near')
 # A tiny counterrotation keeps the head stable instead of a rigid whole-body tilt.
 paste_affine(canvas,parts['head'],(156,225),(neck[0]-2,neck[1]+3),.44,.02+.035*tuck)
 if debug:
  d=ImageDraw.Draw(canvas)
  for side,color in [('near',(80,223,245,255)),('far',(255,135,100,255))]:
   h,k,a,st=joints[side];sh,el,wr,th=armdata[side]
   for chain in [(h,k,a),(sh,el,wr)]:
    pts=[(int(x*S),int(y*S)) for x,y in chain];d.line(pts,fill=color,width=3*S)
    for x,y in pts:d.ellipse((x-4*S,y-4*S,x+4*S,y+4*S),fill=color)
 return canvas.resize((W,H),Image.Resampling.LANCZOS),joints,armdata


out=P/'jump';out.mkdir(exist_ok=True)
frames=[];previews=[]
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
for n in range(24):
 im,_,_=render(n);im.save(out/f'{n:02d}.png');frames.append(im)
 u=max(0,min(1,(n-4)/15));height=140*4*u*(1-u) if 4<=n<=19 else 0
 bg=Image.new('RGB',(440,640),(18,25,40));d=ImageDraw.Draw(bg)
 d.text((20,16),'JUMP / FIXED HEIGHT / 24 FRAMES',font=font,fill=(242,212,130))
 d.line((12,583,428,583),fill=(65,85,103),width=2)
 bg.paste(im,(0,150-round(height)),im)
 stage='CROUCH' if n<4 else ('RISE' if n<12 else ('FALL' if n<=19 else 'LAND'))
 d.text((20,610),f'{n+1:02d} / 24  |  '+stage,font=font,fill=(171,184,201));previews.append(bg)
assert np.array_equal(np.array(frames[0]),np.array(frames[-1]))
previews[0].save(P/'跳跃.gif',save_all=True,append_images=previews[1:],duration=[60]*4+[50]*16+[60]*3+[280],loop=0,optimize=False)
previews[0].save(P/'跳跃慢放.gif',save_all=True,append_images=previews[1:],duration=130,loop=0,optimize=False)
sheet=Image.new('RGBA',(W*6,H*4))
for n,f in enumerate(frames):sheet.alpha_composite(f,((n%6)*W,(n//6)*H))
sheet.save(P/'jump-24.png')
contact=Image.new('RGB',(W*4,640*2))
for k,n in enumerate([0,3,5,9,12,16,20,23]):contact.paste(previews[n],((k%4)*W,(k//4)*640))
contact.save(P/'关键姿势.png')
print('24 pose frames saved; neutral first/last poses match. Vertical trajectory is separate from sprite poses.')
