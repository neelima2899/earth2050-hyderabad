"""Structural checks only; this is NOT scientific model validation."""
from pathlib import Path
import json
import numpy as np
from model import allocate

root=Path(__file__).resolve().parents[1]
d=json.loads((root/'docs/data/hyderabad.json').read_text())
grid=np.array(d['grid'])
assert len(grid)==d['width']*d['height']==len(d['scores'])
assert set(grid)<=set([0,10,20,30,40,50,60,70,80,90,95,100])
assert np.isfinite(d['scores']).all()
assert (grid==50).any() and (grid==80).any()
for protect in [True,False]:
 previous=0
 for year in [2021,2030,2040,2050]:
  for demand in [0,10,25,45,60]:
   base,future,selected,requested=allocate(d,year,demand,protect)
   assert np.all(future[np.isin(base,[0,50,70,80,90,95])]==base[np.isin(base,[0,50,70,80,90,95])])
   if protect: assert np.all(future[base==10]==10)
   assert len(selected)==np.count_nonzero(future!=base)
   assert np.count_nonzero(future==50)==np.count_nonzero(base==50)+len(selected)
   assert len(selected)<=requested
   if year==2021 or demand==0: assert not len(selected)
  _,_,selected,_=allocate(d,year,25,protect)
  assert len(selected)>=previous
  previous=len(selected)
_,_,a,_=allocate(d,2050,25,True)
_,_,b,_=allocate(d,2050,25,True)
assert np.array_equal(a,b)
print('Data integrity, allocation counts, zero-growth, monotonicity, reproducibility, water/no-data and tree exclusions passed.')
print('Observed generalized grid:',d['height'],d['width'],'built-up km²:',round(np.count_nonzero(grid==50)*.01,2))
