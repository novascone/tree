

from .. import tree_core
import bpy
import random
import time
import numpy as np
from . import interaction
from .materials import mat_nodes
from .utils import convert_to_cart, arc_length, get_speeds, fibonacci_sphere, stratified_random

def register_field_operators(): 
    unregister_field_operators()

    for i, field in enumerate(interaction.field_names):
        vis_cls = type(f'TREE_OT_visualization_operator_{i}', (bpy.types.Operator,), {
            'bl_label': f'Visualize Streamlines',
            'bl_idname': f'tree.visualize_{i}',
            'execute': viz_execute_factory(i),
        })

        op_cls = type(f'TREE_OT_computation_operator_{i}', (bpy.types.Operator,), {
            'bl_label': f'Compute Streamlines',
            'bl_idname': f'tree.compute_{i}',
            'execute': comp_execute_factory(i),
        })
        bpy.utils.register_class(vis_cls)
        bpy.utils.register_class(op_cls)
        interaction._field_operators.append(vis_cls)
        interaction._field_operators.append(op_cls)
        

def unregister_field_operators():
    for operator in interaction._field_operators:
        bpy.utils.unregister_class(operator)
    interaction._field_operators.clear()


def viz_execute_factory(idx):
    def execute(self, context):
        n = len([c for c in bpy.data.collections if c.name.startswith('run_')])
        streamline_collection = bpy.data.collections.new(f'run_{n}')
        bpy.context.scene.collection.children.link(streamline_collection)
        alt_min = context.scene.tree_field_props[idx].alt_min
        alt_step = context.scene.tree_field_props[idx].alt_step
        alt_max = context.scene.tree_field_props[idx].alt_max 
        alts = [alt_min] 
        while alts[-1] + alt_step <= alt_max + 1e-6:
            alts.append(alts[-1] + alt_step)
        t_mat = 0.0
        t_points = 0.0
        for i, alt in enumerate(alts):
            t0 = time.perf_counter()
            mat = mat_nodes(context, i, idx)
            t_mat += time.perf_counter() - t0
            alt_collection = bpy.data.collections.new(f'{alts[i]}_km')
            streamline_collection.children.link(alt_collection) 
            
            alt_streams = [s for s in interaction.streamlines[idx] if len(s) > 0.0 and abs(s[0][2] - alt) < 0.01]

            lats_np = np.array([p[0] for s in alt_streams for p in s])
            lons_np = np.array([p[1] for s in alt_streams for p in s])
            alts_np = np.array([p[2] for s in alt_streams for p in s])

            positions = np.stack([lats_np, lons_np, alts_np], axis=1)
            speeds = get_speeds(positions, idx)
            normalized_speeds = np.zeros(len(speeds))
            if speeds.max() != 0:
                normalized_speeds = speeds / speeds.max() 
            
            x, y, z = convert_to_cart(lats_np, lons_np, alts_np)
            flat_x_y_z = np.stack([x, y, z], axis=1).flatten()

            t0 = time.perf_counter()

            curve_data = bpy.data.hair_curves.new(f'alt{alt}_curves')
            curve_data.add_curves([len(s) for s in alt_streams]) 
            arc_attr = curve_data.attributes.new('arc_param', 'FLOAT', 'POINT')
            radius_attr = curve_data.attributes.new('radius', 'FLOAT', 'POINT')
            phase_attr = curve_data.attributes.new('phase', 'FLOAT', 'CURVE') 
            speed_attr = curve_data.attributes.new('speed', 'FLOAT', 'POINT')
             
            flat_phase = np.array([random.random() for s in alt_streams])
            total_points = sum(len(s) for s in alt_streams)
            flat_radius = np.full(total_points, 0.1)
            curve_data.position_data.foreach_set('vector', flat_x_y_z)
            phase_attr.data.foreach_set('value', flat_phase)
            radius_attr.data.foreach_set('value', flat_radius)
            speed_attr.data.foreach_set('value', normalized_speeds)

            arc_segments = []
            for s in alt_streams:
                pts = np.stack(convert_to_cart(
                               np.array([p[0] for p in s]),
                               np.array([p[1] for p in s]),
                               np.array([p[2] for p in s])
                ), axis=1)
                lens = arc_length(pts)
                arc_segments.append(lens / lens[-1])
            flat_arc = np.concatenate(arc_segments)

            arc_attr.data.foreach_set('value', flat_arc)


            obj = bpy.data.objects.new(f'alt_{alt}_km', curve_data)
            obj.data.materials.append(mat)
            alt_collection.objects.link(obj)
            t_points += time.perf_counter() - t0
            
        print(f"mat: {t_mat:.3f}s points: {t_points:.3f}s")
        return {'FINISHED'}
    return execute

def comp_execute_factory(idx): 
    def execute(self, context): 
        props = context.scene.tree_field_props[idx]
        alt = props.alt_min
        seeds = []
        if props.seeding_mode == 'FIBONACCI':
            fib = fibonacci_sphere(props.seeds_per_level)  
            while alt <= props.alt_max + 1e-6:
                for lat, lon in fib:
                    seeds.append([lat, lon, alt])
                alt += props.alt_step
        elif props.seeding_mode == 'STRATIFIED':
            strat = stratified_random(props.lat_cell, props.lon_cell, props.alt_cell, 90, -90, 180, -180,
                                      props.alt_max, props.alt_min)
            seeds = strat
        
            #seeds = [[lat, lon, 86.0] for lat in range(0, 31, 6) for lon in range(0, 31, 6)]
        t0 = time.perf_counter()
        interaction.streamlines[idx] = tree_core.driveField(interaction.read[idx], seeds, props.interval_start, props.interval_end, props.step_size)
        t1 = time.perf_counter()
        print(f"Integration: {t1 - t0:.3f}s")
        return {'FINISHED'}
    return execute

def gen_field_lines_viz(context, idx):
    n = len([c for c in bpy.data.collections if c.name.startswith('run_')])
    streamline_collection = bpy.data.collections.new(f'run_{n}')
    bpy.context.scene.collection.children.link(streamline_collection)
    t_mat = 0.0
    t_points = 0.0 
    t0 = time.perf_counter()
    mat = mat_nodes(context, n, idx)
    t_mat += time.perf_counter() - t0
            
    x = np.array([p[0] for s in interaction.streamlines[idx] for p in s])
    y = np.array([p[1] for s in interaction.streamlines[idx] for p in s])
    z = np.array([p[2] for s in interaction.streamlines[idx] for p in s])
 
    flat_x_y_z = np.stack([x, y, z], axis=1).flatten()

    t0 = time.perf_counter()

    curve_data = bpy.data.hair_curves.new(f'curves')
    curve_data.add_curves([len(s) for s in interaction.streamlines[idx]]) 
    arc_attr = curve_data.attributes.new('arc_param', 'FLOAT', 'POINT')
    radius_attr = curve_data.attributes.new('radius', 'FLOAT', 'POINT')
    phase_attr = curve_data.attributes.new('phase', 'FLOAT', 'CURVE') 
             
    flat_phase = np.array([random.random() for s in interaction.streamlines[idx]])
    total_points = sum(len(s) for s in interaction.streamlines[idx])
    flat_radius = np.full(total_points, 0.1)
    curve_data.position_data.foreach_set('vector', flat_x_y_z)
    phase_attr.data.foreach_set('value', flat_phase)
    radius_attr.data.foreach_set('value', flat_radius)
    
    arc_segments = []
    for s in interaction.streamlines[idx]:
        pts = np.stack([
                        np.array([p[0] for p in s]),
                        np.array([p[1] for p in s]),
                        np.array([p[2] for p in s])] , axis=1)
        lens = arc_length(pts)
        arc_segments.append(lens / lens[-1])
    flat_arc = np.concatenate(arc_segments)

    arc_attr.data.foreach_set('value', flat_arc)


    obj = bpy.data.objects.new(f'curve', curve_data)
    obj.data.materials.append(mat)
    streamline_collection.objects.link(obj)
    t_points += time.perf_counter() - t0
            
    print(f"mat: {t_mat:.3f}s points: {t_points:.3f}s")
    return {'FINISHED'}



