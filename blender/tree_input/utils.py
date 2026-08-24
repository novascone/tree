
from . import interaction
import math
import numpy as np

def fibonacci_sphere(n, level_min, level_max, level_step, geometric_parameters):
    golden = (1 + math.sqrt(5)) / 2
    R = geometric_parameters["radius"]
    points = []
    levels = [level_min]
    while levels[-1] + level_step <= level_max + 1e-6:
        levels.append(levels[-1] + level_step)
    for level in levels:
        for i in range(n):
            theta = 2 * math.pi * i /golden
            phi = math.acos(1 - 2 * (i + 0.5) / n)
            x = math.sin(phi) * math.cos(theta) * (R + level)
            y = math.sin(phi) * math.sin(theta) * (R + level)
            z = math.cos(phi) * (R + level)
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

def stratified_random_sphere(row_cell, arc_per_row, z_max, z_min, geometric_parameters):

    R = geometric_parameters["radius"]  
    r_out = z_max + R
    r_in = z_min + R
    n_rows = math.ceil(2*r_out / row_cell)
    row_idx = np.arange(n_rows)
    z_rows = -r_out + row_idx * row_cell 
    
    coords = []
    for z in z_rows:
        z_center = z + row_cell/2
        ro = math.sqrt(max(0, r_out**2 - z_center**2)) 
        n_theta_row = math.ceil(2*math.pi * ro / arc_per_row)
        z_points = z + np.random.uniform(0, row_cell, n_theta_row)
        mask = (z_points >= -r_out) & (z_points <= r_out)
        z_points = z_points[mask]
        ro_points = np.sqrt(np.maximum(0, r_out**2 - z_points**2))
        u = np.random.uniform(0, 1, len(z_points))
        r_point = (u*(r_out**3 - r_in**3) + r_in**3)**(1/3)
        theta_idx = np.arange(n_theta_row)
        theta_idx = theta_idx[mask]
        if (n_theta_row != 0):
            step = 2*math.pi / n_theta_row
        else:
            step = 0.0 
        theta = theta_idx * step 
        theta += np.random.uniform(0, step, len(theta_idx))
        x = ro_points*np.cos(theta)
        y = ro_points*np.sin(theta)
        scale = r_point / r_out
        x *= scale
        y *= scale
        z_points *= scale
        coords.append(np.stack([x, y, z_points], axis=1))
        
    coords = np.concatenate(coords)
        
    return coords


def strat_sphere_args(type, props, geometric_parameters):
    if type == "vec":
        return [props.vec_lat_cell, props.vec_lon_cell, props.vec_alt_max, props.vec_alt_min, geometric_parameters]
    else:
        return [props.sca_lat_cell, props.sca_lon_cell, props.sca_alt_max, props.sca_alt_min, geometric_parameters]

def fib_sphere_args(type, props, geometric_parameters):
    if type == "vec":
        return [props.seeds_per_level, props.vec_alt_min, props.vec_alt_max, props.vec_alt_step, geometric_parameters]
    else :
        return [props.seeds_per_level, props.sca_alt_min, props.sca_alt_max, props.sca_alt_step, geometric_parameters]


 


def convert_to_cart(lats, lons, alts): 
    R = 6371000.0
    r = (R + alts) / R
    x = r * np.cos(lats) * np.cos(lons)
    y = r * np.cos(lats) * np.sin(lons)
    z = r * np.sin(lats)

    return x, y, z

def get_sphere_level(x, y, z, geometric_parameters):
    R = geometric_parameters["radius"] 
    return (math.sqrt(x**2 + y**2 + z**2) - R)

def arc_length(points):
    diffs = np.diff(points, axis=0)
    norms = np.linalg.norm(diffs, axis=1)
    length = np.concatenate([[0.0], np.cumsum(norms)])
    return length

level_dispatch = {
    'sphere' : get_sphere_level 
}

def leveling_dispatch(geometry):
    return level_dispatch[geometry]

seed_dispatch = {
        ('stratified', 'sphere') : stratified_random_sphere,
        ('fibonacci', 'sphere') : fibonacci_sphere,
}

def seeding_dispatch(seeding_type, geometry) :
        
    return seed_dispatch[(seeding_type, geometry)]

args = {
    ('stratified', 'sphere') : strat_sphere_args,
    ('fibonacci', 'sphere') : fib_sphere_args,
}

def args_dispatch(seeding_type, geometry):
    
    return args[(seeding_type, geometry)]

def distance_from(x, y, z):
    return math.sqrt(x**2 + y**2 + z**2)

