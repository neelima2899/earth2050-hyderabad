"""Create a social preview from the real grid, with an explicitly simulated layer."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from model import allocate
root=Path(__file__).resolve().parents[1]
d=json.loads((root/'dist/data/hyderabad.json').read_text())
base,future,selected,_=allocate(d,2050,25,True)
shown=future.astype(int);shown[selected]=200
palette={0:'#101c1a',10:'#2c6349',20:'#62825a',30:'#7a9465',40:'#657d4e',50:'#dbb384',60:'#82806a',70:'#e3e5dd',80:'#5799b6',90:'#4e8873',95:'#3d6d60',100:'#8d9876',200:'#a7e56d'}
colors=np.zeros((len(shown),3),dtype=np.uint8)
for v,hex in palette.items():
 colors[shown==v]=[int(hex[i:i+2],16) for i in (1,3,5)]
mapimg=Image.fromarray(colors.reshape(d['height'],d['width'],3)).resize((505,500),Image.Resampling.NEAREST)
im=Image.new('RGB',(1200,630),'#101c1a');im.paste(mapimg,(660,60));dr=ImageDraw.Draw(im)
def font(size,bold=False):
 return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',size)
dr.text((45,43),'earth2050 / HYDERABAD',font=font(20,True),fill='#c7f186')
dr.text((45,125),'One city.',font=font(58,True),fill='#f1f1e7')
dr.text((45,205),'A thousand',font=font(54,True),fill='#f1f1e7')
dr.text((45,280),'what ifs.',font=font(58,True),fill='#c7f186')
dr.text((45,390),'Real satellite-derived land cover.',font=font(21),fill='#d1dacb')
dr.text((45,425),'Your growth assumptions.',font=font(21),fill='#d1dacb')
dr.text((45,485),'Explore a possible 2050 →',font=font(23,True),fill='#c7f186')
dr.rectangle((660,60,1165,98),fill='#101c1a');dr.text((675,70),'2021 baseline + illustrative 2050 growth',font=font(16),fill='#f1f1e7')
dr.text((45,575),'Neelima Donkada · ESA WorldCover 2021 · Rule-based experiment, not a prediction',font=font(15),fill='#a3b4a8')
im.save(root/'dist/social.png')
print('Created social preview')
