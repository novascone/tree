

from .. import tree_core
from . import interaction
import math
import numpy as np

def fibonacci_sphere(n):
    golden = (1 + math.sqrt(5)) / 2
    points = []
    for i in range(n):
        theta = 2 * math.pi * i /golden
        phi = math.acos(1 - 2 * (i + 0.5) / n)
        lat = math.degrees(math.pi / 2 - phi)
        lon = math.degrees(theta % (2 * math.pi)) - 180
        points.append((lat, lon))
    return points

def stratified_random(lat_cell, lon_cell, alt_cell, lat_max, lat_min, lon_max, lon_min, alt_max, alt_min):
    n_lat = math.ceil((lat_max - lat_min) / lat_cell)
    n_lon = math.ceil((lon_max - lon_min) / lon_cell)
    n_alt = math.ceil((alt_max - alt_min) / alt_cell)
    
    lat_idx_arr = np.arange(n_lat)
    lon_idx_arr = np.arange(n_lon)
    if n_alt == 0:
        lat, lon = np.meshgrid(lat_idx_arr, lon_idx_arr, indexing='ij')
        lat, lon = lat.ravel(), lon.ravel()
        n = n_lat * n_lon 
        lats = -90 + lat * lat_cell + np.random.uniform(0, lat_cell, n)
        lons = -180 + lon * lon_cell + np.random.uniform(0, lon_cell, n)
        alts = np.full(n, alt_min) 
        seeds = np.stack([lats, lons, alts], axis=1)

    else:
        alt_idx_arr = np.arange(n_alt)
        lat, lon, alt = np.meshgrid(lat_idx_arr, lon_idx_arr, alt_idx_arr, indexing='ij')
        lat, lon, alt = lat.ravel(), lon.ravel(), alt.ravel()
        n = n_lat * n_lon * n_alt 
        lats = -90 + lat * lat_cell + np.random.uniform(0, lat_cell, n)
        lons = -180 + lon * lon_cell + np.random.uniform(0, lon_cell, n)
        alts = alt_min + alt * alt_cell + np.random.uniform(0, alt_cell, n)
        seeds = np.stack([lats, lons, alts], axis=1)
    seeds = seeds.tolist()
    return seeds


def convert_to_cart(lats, lons, alts):
    lat_r = np.radians(lats)
    lon_r = np.radians(lons)
    R = 6371000.0
    r = (R + alts) / R
    x = r * np.cos(lat_r) * np.cos(lon_r)
    y = r * np.cos(lat_r) * np.sin(lon_r)
    z = r * np.sin(lat_r)

    return x, y, z

def arc_length(points):
    diffs = np.diff(points, axis=0)
    norms = np.linalg.norm(diffs, axis=1)
    lengths= np.concatenate([[0.0], np.cumsum(norms)])
    return lengths

def get_speeds(positions, idx):
    tri_interp = tree_core.TriInterp(interaction.read[idx])
    speeds = np.zeros(len(positions))
    for i, pos in enumerate(positions):
        speeds[i] = np.linalg.norm(tri_interp.interp(pos))
    return speeds



