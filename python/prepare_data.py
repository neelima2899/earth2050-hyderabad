"""Read real ESA WorldCover, generalize to 100 m, and export a browser dataset.
Run from the project root: python python/prepare_data.py
"""
from pathlib import Path
import json
import os
import hashlib
import urllib.request
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling, transform_bounds, transform
from rasterio.transform import from_origin
from rasterio.windows import from_bounds
from scipy.ndimage import distance_transform_edt, uniform_filter

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N15E078_Map.tif'
BBOX = [78.25, 17.22, 78.65, 17.60]  # west, south, east, north; urban study window, not GHMC
LOCAL = Path(os.environ.get('WORLDCOVER_LOCAL', 'raw_worldcover_tile.tif'))

def main():
    local = LOCAL
    if not local.exists():
        local = ROOT/'.cache/worldcover_tile.tif'
        local.parent.mkdir(parents=True, exist_ok=True)
        if not local.exists():
            print('Downloading public ESA tile (~116 MB) with HTTPS verification...')
            partial = local.with_suffix('.partial')
            urllib.request.urlretrieve(URL, partial)
            partial.replace(local)
    env = {'GDAL_DISABLE_READDIR_ON_OPEN': 'EMPTY_DIR', 'GDAL_HTTP_TIMEOUT': '90'}
    if Path('/etc/ssl/certs/ca-certificates.crt').exists():
        env['CURL_CA_BUNDLE'] = '/etc/ssl/certs/ca-certificates.crt'
    with rasterio.Env(**env):
        with rasterio.open(local) as src:
            window = from_bounds(*BBOX, src.transform).round_offsets().round_lengths()
            source = src.read(1, window=window)
            source_transform = src.window_transform(window)
            bounds = transform_bounds('EPSG:4326', 'EPSG:32644', *BBOX, densify_pts=21)
            left, bottom, right, top = bounds
            resolution = 100
            width = int(np.ceil((right-left)/resolution))
            height = int(np.ceil((top-bottom)/resolution))
            affine = from_origin(left, top, resolution, resolution)
            grid = np.zeros((height, width), dtype=np.uint8)
            reproject(source, grid, src_transform=source_transform, src_crs=src.crs,
                      dst_transform=affine, dst_crs='EPSG:32644',
                      src_nodata=0, dst_nodata=0, resampling=Resampling.mode)
    built = grid == 50
    # Scores are an illustrative rule, not a trained ML model.
    distance = distance_transform_edt(~built)
    density = uniform_filter(built.astype(float), size=15, mode='constant')
    rng = np.random.default_rng(42)
    score = distance - density * 7 + rng.uniform(0, .05, grid.shape)
    landmarks = [('Hussain Sagar',78.474,17.424),('Charminar',78.4747,17.3616),
                 ('HITEC City',78.377,17.447),('Secunderabad',78.501,17.439),
                 ('Osman Sagar',78.296,17.381)]
    points = []
    for name, lon, lat in landmarks:
        xs, ys = transform('EPSG:4326','EPSG:32644',[lon],[lat])
        points.append({'name':name,'x':(xs[0]-left)/100,'y':(top-ys[0])/100})
    data = {'width':width,'height':height,'cellAreaKm2':.01,'resolutionMetres':100,
            'baselineYear':2021,'bboxLonLat':BBOX,'crs':'EPSG:32644',
            'transform':list(affine)[:6], 'sourceUrl':URL,
            'sourceTitle':'ESA WorldCover 2021 v200',
            'sourceResolutionMetres':10,'resampling':'mode',
            'description':'Hyderabad urban study window, not an administrative boundary',
            'attribution':'© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium',
            'license':'CC BY 4.0','grid':grid.ravel().tolist(),
            'scores':np.round(score.ravel(),3).tolist(),'landmarks':points}
    output = ROOT/'dist/data/hyderabad.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,separators=(',',':')))
    print(json.dumps({'shape':[height,width], 'classes':{str(v):int((grid==v).sum()) for v in np.unique(grid)},
                      'outputBytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))

if __name__ == '__main__':
    main()
