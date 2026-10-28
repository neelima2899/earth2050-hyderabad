# Earth 2050 · Hyderabad thought experiment

An interactive explorer with **real ESA WorldCover 2021 v200 satellite-derived land cover** and a clearly separated, rule-based future growth scenario. It is not a trained or validated forecasting model.

## Run in VS Code on Windows

Unzip the Python starter into a project folder, open that folder in VS Code, and use its terminal:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r python/requirements.txt
.\.venv\Scripts\python.exe -m streamlit run python/app.py
```

The observed extracted grid is included, so the app runs without Google Earth Engine, credentials or a new satellite download. The browser dashboard can also be served from `dist/` with any static HTTP server.

## Files

- `python/prepare_data.py`: extract the source WorldCover tile, reproject with mode resampling to 100 m UTM 44N, generate suitability scores, and save JSON.
- `python/app.py`: local Streamlit explorer using the same data and ranking rule.
- `dist/data/hyderabad.json`: actual extracted WorldCover grid, metadata, and precomputed rule scores.
- `dist/index.html`, `dist/app.js`, `dist/style.css`: hosted browser experience.
- `python/check_data.py`: structural and allocation-invariant checks, not scientific validation.

## Recreate the data

Run `python python/prepare_data.py` from the project root. The script downloads and caches the public ESA tile with verified HTTPS, then reads it locally. Alternatively, set `WORLDCOVER_LOCAL` to an already downloaded tile. Never disable certificate checks. The source tile is approximately 116 MB; it is not included.

## Data and method

Source: ESA WorldCover 10 m 2021 v200, tile N15E078. Study bbox: 78.25–78.65 E, 17.22–17.60 N. This rectangular urban study window is not GHMC or another administrative boundary. No-data margins are excluded from area statistics. The working grid is 100 m in EPSG:32644; each classified cell is 0.01 km². Mode resampling can remove small features and alter proportions relative to native 10 m data.

Growth demand is a user-selected increase relative to the 2021 built-up footprint, interpolated linearly over 2021–2050. Eligible cells are ranked once by distance to existing development minus 7 times the fraction built-up in a 15×15-cell (1.5 km-wide) neighborhood, plus a small seeded tie-breaker. It is a heuristic, not ML. Mapped water, wetlands, snow and no-data are excluded. The tree switch also excludes class 10. Demand is capped by eligible land; unfilled demand is reported.

Do not label the baseline 2025. There is no 2000 baseline here. There is no independent validation, historical trend estimation, individual house count, climate model, flood model, zoning or population model. Future land cover is conditional on the assumptions. Water remains stable because the rule explicitly protects it, not because we predicted water stability.

## Attribution

© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium.

Dataset license: CC BY 4.0. Source: https://esa-worldcover.org/en/data-access
Dataset citation: Zanaga et al. (2022), ESA WorldCover 10 m 2021 v200. https://doi.org/10.5281/zenodo.7254221

## Sharing

Suggested description: “An interactive Python-powered thought experiment using real satellite-derived land cover to explore how different growth assumptions could reshape Hyderabad.” Do not present the scenarios as validated predictions.
