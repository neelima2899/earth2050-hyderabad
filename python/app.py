"""Local explorer using the same real data and allocation rule as the website.
Run: python -m streamlit run python/app.py
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title='Earth 2050 | Hyderabad', page_icon='🌍', layout='wide')

@st.cache_data
def load_data():
    return json.loads((ROOT/'dist/data/hyderabad.json').read_text())

from model import allocate

st.title('🌍 Earth 2050 · Hyderabad')
st.info('Real satellite-derived baseline: ESA WorldCover 2021. Future layer: a rule-based thought experiment, not a trained or validated prediction.')
data = load_data()
year = st.sidebar.slider('Scenario year', 2021, 2050, 2050)
demand = st.sidebar.slider('Extra built-up footprint by 2050 (%)', 0, 60, 25, 5)
protect = st.sidebar.checkbox('Keep mapped tree cover', value=True)
st.sidebar.caption('Growth is an assumption relative to 2021 built-up area. Water and wetlands are always excluded.')
base, future, selected, requested = allocate(data, year, demand, protect)
st.metric('Additional built-up area', f'{len(selected)*.01:.1f} km²')
if len(selected) < requested:
    st.warning(f'{(requested-len(selected))*.01:.1f} km² requested growth cannot fit within eligible land.')
shape = (data['height'],data['width'])
codes = [0,10,20,30,40,50,60,70,80,90,95,100,200]
colors = ['#192824','#2c6349','#62825a','#7a9465','#657d4e','#dbb384','#82806a','#e3e5dd','#5799b6','#4e8873','#3d6d60','#8d9876','#a7e56d']
lookup = {v:i for i,v in enumerate(codes)}
shown = future.astype(np.int16).copy()
shown[selected] = 200
fig, axes = plt.subplots(1,2,figsize=(13,7))
for ax, values, title in zip(axes,[base,shown],['2021 · Observed classification',f'{year} · Assumption-driven scenario']):
    display = np.array([lookup.get(int(v),0) for v in values]).reshape(shape)
    ax.imshow(display,cmap=ListedColormap(colors),vmin=-.5,vmax=len(codes)-.5,interpolation='nearest')
    ax.set_title(title)
    ax.set_axis_off()
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.caption('Beige: existing built-up · Bright green: simulated new built-up · Greens: vegetation/crops · Blue: water · Gray: other')
summary = []
for label, values in [('Built-up',[50]),('Vegetation & crops',[10,20,30,40,90,95,100]),('Water',[80]),('Other',[60,70])]:
    summary.append({'Category':label,'2021 km²':np.isin(base,values).sum()*.01,
                    f'{year} scenario km²':np.isin(future,values).sum()*.01})
table = pd.DataFrame(summary).set_index('Category')
st.dataframe(table)
st.bar_chart(table)
st.download_button('Download results CSV',table.to_csv().encode(),file_name=f'hyderabad_scenario_{year}.csv',mime='text/csv')
with st.expander('Method and limitations', expanded=True):
    st.write('Python generalizes original 10 m WorldCover classes to a 100 m UTM grid using mode resampling. The study window is 78.25–78.65° E, 17.22–17.60° N; it is not the official Hyderabad boundary. Percentages and areas refer to generalized cells, not native 10 m measurements.')
    st.write('The allocation score is distance to 2021 built-up cells minus 7 times neighborhood built-up fraction, plus a small seeded tie-breaker. Lower scores fill first. The expansion budget is linear over 2021–2050; growth locations are ranked once, not retrained each year.')
    st.write('Mapped water, wetlands, snow and no-data are excluded. The tree switch excludes class 10. Water conservation is imposed, not predicted. We do not model zoning, housing counts, population, floods or climate. This is not historical back-testing or a validated forecast.')
    st.write(data['attribution'])
    st.write('Source: '+data['sourceUrl'])
