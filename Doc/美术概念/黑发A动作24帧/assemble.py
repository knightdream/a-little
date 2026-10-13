from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math,json
root=Path(__file__).resolve().parent
bounds={'walk':[0,334,646,952,1254],'jump':[0,328,645,946,1254],'attack':[0,228,459,697,931,1160]}
all_frames={}
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',23)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
for action,ys in bounds.items():
 im=Image.open(root/'源图'/('attack-wide.png' if action=='attack' else f'{action}.png')).convert('RGBA')
 target=root/action;target.mkdir(exist_ok=True)
 frames=[]
 for n in range(24):
  source_n=([0,0,1,2,3,4,5,6,7,8,9,10,11,12,12,13,14,15,16,17,18,19,19,19][n] if action=='attack' else n)
  columns=4 if action=='attack' else 6
  row,col=divmod(source_n,columns)
  tile=im.crop((round(col*im.width/columns),ys[row],round((col+1)*im.width/columns),ys[row+1]))
  alpha=tile.getchannel('A');box=alpha.point(lambda v:255 if v>80 else 0).getbbox()
  sprite=tile.crop(box)
  # Stable floor pivot from the opaque foot pixels, retaining the generated pose.
  a=sprite.getchannel('A'); coords=[]
  for y in range(max(0,sprite.height-12),sprite.height):
   for x in range(sprite.width):
    if a.getpixel((x,y))>160: coords.append(x)
  pivot=sum(coords)/len(coords) if coords else sprite.width/2
  scale=1.43 if action=='attack' else .90
  sprite=sprite.resize((round(sprite.width*scale),round(sprite.height*scale)),Image.Resampling.LANCZOS)
  lift=0
  if action=='jump' and 5<=n<=18: lift=round(76*math.sin(math.pi*(n-5)/13))
  frame=Image.new('RGBA',(400,400))
  frame.alpha_composite(sprite,(round(200-pivot*scale),340-lift-sprite.height))
  frame.save(target/f'{n:02d}.png')
  frames.append(frame)
 sheet=Image.new('RGBA',(2400,1600))
 for n,f in enumerate(frames):sheet.alpha_composite(f,((n%6)*400,(n//6)*400))
 sheet.save(root/f'{action}-24.png')
 all_frames[action]=frames
 previews=[]
 for n,f in enumerate(frames):
  bg=Image.new('RGB',(400,400),(18,25,40));d=ImageDraw.Draw(bg)
  d.line((20,341,380,341),fill=(67,84,105),width=2)
  bg.paste(f,(0,0),f);d.text((20,15),action.upper(),font=font,fill=(234,232,223))
  d.text((20,372),f'{n+1:02d} / 24',font=small,fill=(165,176,192));previews.append(bg)
 previews[0].save(root/f'{action}.gif',save_all=True,append_images=previews[1:],duration=80,loop=0,optimize=False)
combined=[]
for n in range(24):
 bg=Image.new('RGB',(1200,440),(18,25,40));d=ImageDraw.Draw(bg)
 for k,action in enumerate(bounds):
  x=k*400;d.text((x+20,18),action.upper(),font=font,fill=(244,216,130))
  d.line((x+20,371,x+380,371),fill=(67,84,105),width=2)
  f=all_frames[action][n];bg.paste(f,(x,30),f)
  d.text((x+20,409),f'FRAME {n+1:02d} / 24',font=small,fill=(165,176,192))
 combined.append(bg)
combined[0].save(root/'动作并排预览.gif',save_all=True,append_images=combined[1:],duration=80,loop=0,optimize=False)
combined[12].save(root/'预览检查.png')
(root/'metadata.json').write_text(json.dumps({'framesPerAction':24,'previewFps':12.5,'frameSize':[400,400],'sheetColumns':6,'sheetRows':4,'actions':list(bounds),'note':'Generated concept animation; jump preview adds display-only vertical trajectory, not game physics.'},indent=2))
print('Created 72 RGBA frames, 3 sheets and 4 GIF previews.')
