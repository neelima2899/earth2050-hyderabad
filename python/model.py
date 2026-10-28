"""Deterministic allocation rule. No ML training or prediction accuracy claim."""
import numpy as np

def allocate(data, year, demand, protect_trees):
    grid = np.array(data['grid'], dtype=np.uint8)
    scores = np.array(data['scores'])
    eligible = ~np.isin(grid, [0, 50, 70, 80, 90, 95])
    if protect_trees:
        eligible &= grid != 10
    indices = np.flatnonzero(eligible)
    ranked = indices[np.argsort(scores[indices], kind='stable')]
    requested = int(np.floor(np.count_nonzero(grid == 50)*demand/100*(year-2021)/29))
    selected = ranked[:requested]
    future = grid.copy()
    future[selected] = 50
    return grid, future, selected, requested

