
from .. import tree_core
import bpy
import os
import random
import time
import math
import numpy as np
import openvdb as vdb
from . import interaction
from .materials import mat_nodes, sca_mat_nodes, volume_mat_nodes
from .utils import convert_to_cart, arc_length, fibonacci_sphere, stratified_random, leveling_dispatch, seeding_dispatch, args_dispatch, distance_from

def register_field_operators(): 
    unregister_field_operators()

    for i, field in enumerate(interaction.field_names):
        field_type = interaction.tree_config.fields[i].type
        if field_type == "vector":
            vis_cls = type(f'TREE_OT_visualization_operator_{i}', (bpy.types.Operator,), {
                'bl_label': f'Visualize Streamlines',
                'bl_idname': f'tree.visualize_vector_{i}',
                'execute': vec_viz_execute_factory(i),
            })

            op_cls = type(f'TREE_OT_computation_operator_{i}', (bpy.types.Operator,), {
                'bl_label': f'Compute Streamlines',
                'bl_idname': f'tree.compute_{i}',
                'execute': vec_comp_execute_factory(i),
            })
            vol_class = type(f'TREE_OT_point_cloud_field_{i}', (bpy.types.Operator,), {
                'bl_label': f'Point Cloud Field',
                'bl_idname': f'tree.point_cloud_field_{i}',
                'execute': point_cloud_field_execute_factory(i),
            })
            bpy.utils.register_class(vis_cls)
            bpy.utils.register_class(op_cls)
            bpy.utils.register_class(vol_class)
            interaction._field_operators.append(vis_cls)
            interaction._field_operators.append(op_cls)
            interaction._field_operators.append(vol_class)
        elif field_type == "scalar":
            vis_cls = type(f'TREE_OT_visualization_operator_{i}', (bpy.types.Operator,), {
                'bl_label': f'Visualize Scalar',
                'bl_idname': f'tree.visualize_scalar_{i}',
                'execute': sca_viz_execute_factory(i),
            })
            bpy.utils.register_class(vis_cls)
            interaction._field_operators.append(vis_cls) 

        

def unregister_field_operators():
    for operator in interaction._field_operators:
        bpy.utils.unregister_class(operator)
    interaction._field_operators.clear()

def vec_comp_execute_factory(idx): 
    def execute(self, context): 
        props = context.scene.tree_field_props[idx] 
        seeds = []
        seeding_tuple = (props.vec_seeding_mode.lower(), interaction.tree_config.geometry.type.lower())
        seeding = seeding_dispatch(*seeding_tuple)
        seeding_args = args_dispatch(*seeding_tuple)
        args = seeding_args("vec", props, interaction.tree_config.geometry.parameters)
        seeds = seeding(*args)
        #seeds = [[lat, lon, 86.0] for lat in range(0, 31, 6) for lon in range(0, 31, 6)]
        seeds = np.asarray(seeds) 
        t0 = time.perf_counter()
        interaction.streamlines[idx] = tree_core.drive_field(interaction.read[idx], interaction.tree_config.geometry.parameters, seeds, props.interval_start, props.interval_end, props.step_size)
    
        num_empty = 0
        for s in interaction.streamlines[idx]:
            if len(s) == 0:
                num_empty += 1

        if num_empty != 0:
            self.report({'WARNING'}, f"{num_empty}/{len(interaction.streamlines[idx])} streamlines are empty, check seeding against dataset if this is unexpected")

        t1 = time.perf_counter()
        print(f"Integration: {t1 - t0:.3f}s")
        return {'FINISHED'}
    return execute


def vec_viz_execute_factory(idx):
    def execute(self, context):
        n = len([c for c in bpy.data.collections if c.name.startswith('run_')])
        geometric_parameters = interaction.tree_config.geometry.parameters
        streamlines = [s for s in interaction.streamlines[idx] if len(s) > 0.0] 

        if len(streamlines) == 0:
            self.report({'WARNING'}, "Streamlines have no length")
            return {'CANCELLED'}

        streamline_collection = bpy.data.collections.new(f'{interaction.field_names[idx]}_vector_run_{n}')
        bpy.context.scene.collection.children.link(streamline_collection)
        t_mat = 0.0
        t_points = 0.0 
        t0 = time.perf_counter()
        mat = mat_nodes(context, 0, idx)
        t_mat += time.perf_counter() - t0       

        xs_np = np.array([p[0] for s in streamlines for p in s])
        ys_np = np.array([p[1] for s in streamlines for p in s])
        zs_np = np.array([p[2] for s in streamlines for p in s])

        positions = np.stack([xs_np, ys_np, zs_np], axis=1) 
        speeds = tree_core.get_mags(interaction.read[idx], geometric_parameters, positions)
        speeds = np.asarray(speeds)
        normalized_speeds = np.zeros(len(speeds))
        positions = positions / distance_from(*interaction.geometry.positions[0:3]) 
        flat_positions = positions.flatten()

        if len(speeds) > 0:
            percentile_clamp = np.percentile(speeds, 99)
            if percentile_clamp != 0:
                normalized_speeds = np.clip(speeds / percentile_clamp, 0, 1) 
              

        t0 = time.perf_counter()

        curve_data = bpy.data.hair_curves.new(f'{interaction.field_names[idx]}_curves')
        curve_data.add_curves([len(s) for s in streamlines]) 
        arc_attr = curve_data.attributes.new('arc_param', 'FLOAT', 'POINT')
        radius_attr = curve_data.attributes.new('radius', 'FLOAT', 'POINT')
        phase_attr = curve_data.attributes.new('phase', 'FLOAT', 'CURVE') 
        speed_attr = curve_data.attributes.new('speed', 'FLOAT', 'POINT')
             
        flat_phase = np.array([random.random() for s in streamlines])
        total_points = sum(len(s) for s in streamlines)
        flat_radius = np.full(total_points, 0.1)
        curve_data.position_data.foreach_set('vector', flat_positions)
        phase_attr.data.foreach_set('value', flat_phase)
        radius_attr.data.foreach_set('value', flat_radius)
        speed_attr.data.foreach_set('value', normalized_speeds)

        arc_segments = []
        for s in streamlines:
            pts = np.stack((
                           np.array([p[0] for p in s]),
                           np.array([p[1] for p in s]),
                           np.array([p[2] for p in s])), axis=1)
            lens = arc_length(pts)
            arc_segments.append(lens / lens[-1])
        flat_arc = np.concatenate(arc_segments)

        arc_attr.data.foreach_set('value', flat_arc)


        obj = bpy.data.objects.new(f'{interaction.field_names[idx]}_m', curve_data)
        obj.data.materials.append(mat)
        streamline_collection.objects.link(obj)
        t_points += time.perf_counter() - t0
            
        print(f"mat: {t_mat:.3f}s points: {t_points:.3f}s")
        return {'FINISHED'}
    return execute

def point_cloud_field_execute_factory(idx):
    def execute(self, context):
        n = len([c for c in bpy.data.collections if c.name.startswith('run_')]) 
        props = context.scene.tree_field_props[idx]
        point_radius = context.scene.tree_field_props[idx].point_radius 

        seeding_tuple = (props.sca_seeding_mode.lower(), interaction.tree_config.geometry.type.lower())
        seeding = seeding_dispatch(*seeding_tuple)
        seeding_args = args_dispatch(*seeding_tuple)
        args = seeding_args("sca", props, interaction.tree_config.geometry.parameters)
        seeds = seeding(*args)
        positions = np.array(seeds)
        vals = tree_core.get_mags(interaction.read[idx], interaction.tree_config.geometry.parameters, positions)
        vals = np.asarray(vals)

        mask = vals >= props.threshold
        positions = positions[mask]
        vals = vals[mask]

        d = len(vals)

        if d == 0:
            self.report({'WARNING'}, "No points meet the threshold")
            return {'CANCELLED'}

        mat = sca_mat_nodes(context, idx)
        sca_viz_collection = bpy.data.collections.new(f'{interaction.field_names[idx]}_scalar_run_{n}')
        bpy.context.scene.collection.children.link(sca_viz_collection) 
        
 
        flat_x_y_z = np.asarray(positions / distance_from(*interaction.geometry.positions[0:3])).flatten()
        norm_vals = (vals - vals.min()) / (vals.max() - vals.min())


        pc = bpy.data.pointclouds.new('points')
        pc.resize(d)

        pc.points.foreach_set('co', flat_x_y_z) 

        flat_r = np.full(d, point_radius)
        pc.points.foreach_set('radius', flat_r)  
        rad_attr = pc.attributes.new('radiance', 'FLOAT', 'POINT')
        rad_attr.data.foreach_set('value', norm_vals)

        obj = bpy.data.objects.new('scalar_field', pc)
        obj.data.materials.append(mat)
        sca_viz_collection.objects.link(obj)
        return {'FINISHED'}
    return execute

def volumetric_visualization_factory(idx):
    def execute(self, context):
        n = len([c for c in bpy.data.collections if c.name.startswith('run_')])
        volume_collection = bpy.data.collections.new(f'volume_run_{n}')
        bpy.context.scene.collection.children.link(volume_collection)
        props = context.scene.tree_field_props[idx]

        R = 6371000.0
        alt_max = props.alt_max
        alt_min = props.alt_min
        r_max = (R + alt_max) / R
        r_min = (R + alt_min) / R

        voxel_size = 0.00062

        transform = vdb.createLinearTransform(voxelSize=voxel_size)

        grid = vdb.FloatGrid()
        grid.transform = transform
        grid.name = "density"

        accessor = grid.getAccessor()

        N = math.ceil(r_max / voxel_size)


        #ijk = []
        #lla = []

        xy = np.arange(-N, N+1)
        X, Y = np.meshgrid(xy, xy, indexing='ij')
        X = X.ravel()
        Y = Y.ravel()

        x = X * voxel_size
        y = Y * voxel_size
        d = np.sqrt(x**2 + y**2)

        active_mask = d <= r_max

        X = X[active_mask]
        Y = Y[active_mask]
        x = x[active_mask]
        y = y[active_mask]
        d = d[active_mask]

        z_outer = np.sqrt(r_max**2 - d**2) / voxel_size

        one_band_mask = d > r_min
        two_band_mask = ~one_band_mask
        
        z_outer_one = z_outer[one_band_mask]
        z_outer_two = z_outer[two_band_mask]

        del z_outer

        X_one = X[one_band_mask]
        Y_one = Y[one_band_mask]
        x_one = x[one_band_mask]
        y_one = y[one_band_mask]
        d_one = d[one_band_mask]

        X_two = X[two_band_mask]
        Y_two = Y[two_band_mask]
        x_two = x[two_band_mask]
        y_two = y[two_band_mask]
        d_two = d[two_band_mask]

        del X
        del Y
        del x
        del y
        del d

        z_inner = (np.sqrt(r_min**2 - d_two**2)) / voxel_size

        k_bound = np.ceil(z_outer_one).astype(int)
        k_upper = np.ceil(z_outer_two).astype(int)
        k_lower = np.floor(z_inner).astype(int)

        counts_one = 2 * k_bound + 1
        X_one_rep = np.repeat(X_one, counts_one)
        Y_one_rep = np.repeat(Y_one, counts_one)
        x_one_rep = np.repeat(x_one, counts_one)
        y_one_rep = np.repeat(y_one, counts_one)

        starts_one = np.cumsum(counts_one) - counts_one
        starts_one_rep = np.repeat(starts_one, counts_one)

        total = counts_one.sum()
        local = np.arange(total) - starts_one_rep 

        k_one_rep = np.repeat(-k_bound, counts_one) + local

        counts_two = k_upper - k_lower + 1

        X_two_rep = np.repeat(X_two, counts_two)
        Y_two_rep = np.repeat(Y_two, counts_two)
        x_two_rep = np.repeat(x_two, counts_two)
        y_two_rep = np.repeat(y_two, counts_two)

        del X_one
        del X_two
        del Y_one
        del Y_two
        del x_one
        del x_two
        del y_one
        del y_two
        del d_one
        del d_two

        starts_two = np.cumsum(counts_two) - counts_two
        starts_two_rep = np.repeat(starts_two, counts_two)

        total_two = counts_two.sum()
        local_two = np.arange(total_two) - starts_two_rep

        k_two_rep = np.repeat(k_lower, counts_two) + local_two

        X_two_mir = np.concatenate((X_two_rep, X_two_rep))
        Y_two_mir = np.concatenate((Y_two_rep, Y_two_rep))
        x_two_mir = np.concatenate((x_two_rep, x_two_rep))
        y_two_mir = np.concatenate((y_two_rep, y_two_rep)) 
        k_two_mir = np.concatenate((k_two_rep, -k_two_rep))

        X_final = np.concatenate((X_one_rep, X_two_mir))
        del X_one_rep
        del X_two_mir
        Y_final = np.concatenate((Y_one_rep, Y_two_mir))
        del Y_one_rep
        del Y_two_mir
        x_final = np.concatenate((x_one_rep, x_two_mir))
        del x_one_rep
        del x_two_mir
        y_final = np.concatenate((y_one_rep, y_two_mir))
        del y_one_rep
        del y_two_mir
        k_final = np.concatenate((k_one_rep, k_two_mir))
        del k_one_rep
        del k_two_mir
        z_final = k_final * voxel_size

        lat, lon, alt = invert_coords(R, x_final, y_final, z_final)
        XYZ = np.stack((X_final, Y_final, k_final), axis=1)
        lla = np.stack((lat, lon, alt), axis=1)

        del X_final
        del Y_final
        del x_final
        del y_final
        del k_final
        del z_final
        del lat
        del lon
        del alt
 
        #for i in range(-N, N+1):
        #    for j in range(-N, N+1):
        #        x = i * voxel_size
        #        y = j * voxel_size 
        #        d = math.sqrt(x**2 + y**2)
        #        if d > r_max:
        #            continue
        #        elif d > r_min:
        #            z_outer = math.sqrt(r_max**2 - d**2) / voxel_size
        #            k_bound = math.ceil(z_outer)
        #            for k in range(-k_bound, k_bound+1):
        #                ijk.append((i,j,k))
        #                z = k * voxel_size
        #                lat, lon, alt = invert_coords(R, x, y, z)
        #                lla.append((lat, lon, alt))
        #        else:
        #            z_outer = math.sqrt(r_max**2 - d**2) / voxel_size
        #            z_inner = math.sqrt(r_min**2 - d**2) / voxel_size
        #            k_upper = math.ceil(z_outer)
        #            k_lower = math.floor(z_inner)
        #            for k in range(k_lower, k_upper+1):
        #                ijk.append((i,j,k))
        #                z = k * voxel_size
        #                lat, lon, alt = invert_coords(R, x, y, z)
        #                lla.append((lat,lon,alt))
        #            for k in range(-k_upper, -k_lower+1):
        #                ijk.append((i,j,k))
        #                z = k * voxel_size
        #                lat, lon, alt = invert_coords(R, x, y, z)
        #                lla.append((lat, lon, alt))

        #lla = np.array(lla)
        #ijk = np.array(ijk)

        mags = tree_core.get_mags(interaction.read[idx], lla)

        mask = mags >= props.threshold
        XYZ = XYZ[mask] 
        mags = mags[mask]

        d = len(mags)

        if d == 0:
            self.report({'WARNING'}, "No points meet the threshold")
            return {'CANCELLED'}

        mat = volume_mat_nodes(context, idx)

        for coord, mag in zip(XYZ, mags):
            accessor.setValueOn(coord, mag)

        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vdb", str(idx)))
        file_path = os.path.join(path,  "field-volume.vdb")
        os.makedirs(path, exist_ok=True)
        vdb.write(file_path, grids=[grid])
        bpy.ops.object.volume_import(filepath=file_path)
        obj = context.active_object

        for collection in obj.users_collection:
            collection.objects.unlink(obj)
        
        obj.data.materials.append(mat)
        volume_collection.objects.link(obj)

        return {'FINISHED'}
    return execute
        


                            
def invert_coords(R, x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    lat = np.degrees(np.arcsin(z/r))
    lon = np.degrees(np.arctan2(y, x)) % 360
    alt = R * (r - 1)
        
    return lat, lon, alt



def sca_viz_execute_factory(idx):
    def execute(self, context):
        n = len([c for c in bpy.data.collections if c.name.startswith('run_')])  
        mat = sca_mat_nodes(context, idx)
        scalar_collection = bpy.data.collections.new(f'{interaction.field_names[idx]}_scalar_run_{n}')
        bpy.context.scene.collection.children.link(scalar_collection)
        vals = np.array(interaction.read[idx].values[0])
        props = context.scene.tree_field_props[idx]
        point_radius = context.scene.tree_field_props[idx].point_radius
        displacement = context.scene.tree_field_props[idx].displacement
        coord_list = [] 
        for i in range (len(interaction.read[idx].coords)):
            coord_list.append(np.array(interaction.read[idx].coords[i]))
        mask = np.ones(len(vals), dtype=bool)
        for coord in coord_list:
            mask &= ~np.isnan(coord)
        mask &= ~np.isnan(vals)
        coord_list = [coord[mask] for coord in coord_list]
        vals = vals[mask]
        d = len(coord_list[0])
        if interaction.tree_config.fields[idx].altitude is not None:
            coord_list.append(np.full(d, interaction.tree_config.fields[idx].altitude)) 
        

        x, y, z = convert_to_cart(coord_list[0], coord_list[1], coord_list[2]) 
        if displacement:
            displacement_scale = context.scene.tree_field_props[idx].displacement_scale
            r = np.sqrt(x**2 + y**2 + z**2)
            nudge = (vals - vals.mean()) * displacement_scale
            x = x + nudge * (x / r)
            y = y + nudge * (y / r)
            z = z + nudge * (z / r)
        flat_x_y_z = np.stack([x, y, z], axis=1).flatten()
        norm_vals = (vals - vals.min()) / (vals.max() - vals.min())


        pc = bpy.data.pointclouds.new('points')
        pc.resize(d)

        pc.points.foreach_set('co', flat_x_y_z) 

        flat_r = np.full(d, point_radius)
        pc.points.foreach_set('radius', flat_r)  
        rad_attr = pc.attributes.new('radiance', 'FLOAT', 'POINT')
        rad_attr.data.foreach_set('value', norm_vals)

        obj = bpy.data.objects.new('scalar_field', pc)
        obj.data.materials.append(mat)
        scalar_collection.objects.link(obj)
        return {'FINISHED'}
    return execute


def gen_field_lines_viz(context, idx):
    n = len([c for c in bpy.data.collections if c.name.startswith('run_')])
    streamline_collection = bpy.data.collections.new(f'{interaction.field_names[idx]}_run_{n}')
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



