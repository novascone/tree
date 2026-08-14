
from . import interaction
import math
import numpy as np

def fibonacci_sphere(n):
    golden = (1 + math.sqrt(5)) / 2
    points = []
    for i in range(n):
        theta = 2 * math.pi * i /golden
        phi = math.acos(1 - 2 * (i + 0.5) / n)
        x = math.sin(phi) * math.cos(theta)
        y = math.sin(phi) * math.sin(theta)
        z = math.cos(phi)
        points.append((x, y, z))
    return points

def stratified_random(x_cell, y_cell, z_cell, z_max, z_min):

    R = 6371000.0
    n_z = math.ceil((z_max - z_min) / z_cell)
    r_out = R + z_max
    r_in = R + z_min
    n_x = math.ceil((2 * r_out) / x_cell)
    n_y = math.ceil((2 * r_out) / y_cell)
    x_idx_arr = np.arange(n_x)
    y_idx_arr = np.arange(n_y)
    x, y = np.meshgrid(x_idx_arr, y_idx_arr, indexing='ij')
    x, y = x.ravel(), y.ravel()
    n = n_x * n_y 
    xs = -r_out + x * x_cell 
    ys = -r_out + y * y_cell
    xs += np.random.uniform(0, x_cell, n)
    ys += np.random.uniform(0, y_cell, n)
    d = np.sqrt(xs**2 + ys**2)
    mask_out = d <= r_out 
    xs = xs[mask_out]
    ys = ys[mask_out]    
     
    if n_z == 0:
        zs_up = np.sqrt(r_out**2 - xs**2 - ys**2)
        zs_down = -np.sqrt(r_out**2 - xs**2 - ys**2)
        xs = np.concatenate((xs, xs))
        ys = np.concatenate((ys, ys))
        zs = np.concatenate((zs_up, zs_down))
        seeds = np.stack([xs, ys, zs], axis=1)

    else:
        d = np.sqrt(xs**2 + ys**2)
        z_outer = np.sqrt(r_out**2 - xs**2 - ys**2) 
        z_inner = np.sqrt(np.maximum(0, r_in**2 - d**2))
        zs = np.random.uniform(z_inner, z_outer)
        xs = np.concatenate((xs, xs))
        ys = np.concatenate((ys, ys))
        zs = np.concatenate((zs, -zs))
        seeds = np.stack([xs, ys, zs], axis=1)
     
    seeds = seeds.tolist()
    return seeds


def convert_to_cart(lats, lons, alts): 
    R = 6371000.0
    r = (R + alts) / R
    x = r * np.cos(lats) * np.cos(lons)
    y = r * np.cos(lats) * np.sin(lons)
    z = r * np.sin(lats)

    return x, y, z

def get_ro(x, y, z):
    R = 6371000.0
    return (math.sqrt(x**2 + y**2 + z**2) - R)


def arc_length(points):
    diffs = np.diff(points, axis=0)
    norms = np.linalg.norm(diffs, axis=1)
    lengths= np.concatenate([[0.0], np.cumsum(norms)])
    return lengths

