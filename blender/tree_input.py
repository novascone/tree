
from . import tree_core
from .parser.lex import lex
from .parser.parse import parse 
from .parser.validate import validate  
from .parser.convert import convert 
from .parser.translate import translate
from .mesh import build_mesh
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, FloatProperty, IntProperty
from bpy.types import Operator
import bpy
import colorsys
import math
import random
import time
import numpy as np

geometry = None
read = None
streamlines = None

def read_data(input_file):

    global geometry, read
    with open(input_file) as f:
        tokens = lex(f)
        
    root = parse(tokens) 
    validate(root)  
    config = convert(root) 
    tree_config = translate(config) 
    geometry = tree_core.build_mesh(tree_config.geometry) 
    read = tree_core.Read(tree_config.fields[0])
    

class ImportData(Operator, ImportHelper):
    """Import an input .i file"""
    bl_idname = "import.tree_data"
    bl_label = "Import Data"

    filename_ext = ".i"

    filter_glob: StringProperty(default="*.i")

    def execute(self, context):

        try:
            read_data(self.filepath)
            mesh = build_mesh(geometry)
            obj = bpy.data.objects.new(geometry.name, mesh)
            bpy.context.collection.objects.link(obj)
        except ValueError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        return {'FINISHED'} 


def menu_func_import(self, context):
    self.layout.operator(ImportData.bl_idname, text="Import TREE file")


class TREEProperties(bpy.types.PropertyGroup):
    interval_start: FloatProperty(name="Interval Start", default=0.0)
    interval_end: FloatProperty(name="Interval End", default=10800)
    step_size: FloatProperty(name="Step Size", default=0.1)
    anim_speed: FloatProperty(name="Anim Speed", default=0.01, min=0.001, max=1.0)
    spot_width: FloatProperty(name="Spot Width", default=0.1, min=0.01, max=1.0) 
    spot_strength: FloatProperty(name="Spot Strength", default=1.0)
    seeds_per_level: IntProperty(name="Seeds Per Level", default=50, min=1)
    alt_min: FloatProperty(name="Alt Min (km)", default=83.0)
    alt_max: FloatProperty(name="Alt Max (km)", default=90.0)
    alt_step: FloatProperty(name="Alt Step (km)", default=1.0, min=0.1)

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

class ComputeStreamlines(Operator):
    """Get the path for the streamline"""
    bl_idname = "tree.compute_streamlines"
    bl_label = "Compute Streamlines" 

    def execute(self, context):
        global streamlines
        props = context.scene.tree_props
        fib = fibonacci_sphere(props.seeds_per_level)
        alt = props.alt_min
        seeds = []
        while alt <= props.alt_max + 1e-6:
            for lat, lon in fib:
                seeds.append([lat, lon, alt])
            alt += props.alt_step 
        #seeds = [[lat, lon, 86.0] for lat in range(0, 31, 6) for lon in range(0, 31, 6)]
        t0 = time.perf_counter()
        streamlines = tree_core.driveField(read, seeds, props.interval_start, props.interval_end, props.step_size)
        t1 = time.perf_counter()
        print(f"Integration: {t1 - t0:.3f}s")
        return {'FINISHED'}

def convert_to_cart(lats, lons, alts):
    lat_r = np.radians(lats)
    lon_r = np.radians(lons)
    R = 6371.0
    r = (R + alts) / R
    x = r * np.cos(lat_r) * np.cos(lon_r)
    y = r * np.cos(lat_r) * np.sin(lon_r)
    z = r * np.sin(lat_r)

    return x, y, z


def mat_nodes(context, i):
 
    props = context.scene.tree_props
    #streamline_collection['interval_start'] = props.interval_start
    #streamline_collection['interval_end'] = props.interval_end
    #streamline_collection['step_size'] = props.step_size
    mat = bpy.data.materials.new(f'mat_{i}')
    mat.use_nodes = True
    hue = (i * 0.618033988749895) % 1
    r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
  
    attr = nodes.new('ShaderNodeAttribute')
    attr.attribute_name = 'arc_param'
    attr.attribute_type = 'GEOMETRY'
    spot_pos = nodes.new('ShaderNodeValue')

    phase = nodes.new('ShaderNodeAttribute')
    phase.attribute_name = 'phase'
    phase.attribute_type = 'GEOMETRY'

    add_phase = nodes.new('ShaderNodeMath')
    add_phase.operation = 'ADD'

    modulo = nodes.new('ShaderNodeMath')
    modulo.operation = 'MODULO'
    modulo.inputs[1].default_value = 1.0
    
    # distance = abs(factor - spot_pos)
    subtract = nodes.new('ShaderNodeMath')
    subtract.operation = 'SUBTRACT'

    absolute = nodes.new('ShaderNodeMath')
    absolute.operation = 'ABSOLUTE'

    minimum = nodes.new('ShaderNodeMath')
    minimum.operation = 'MINIMUM'

    subtract2 = nodes.new('ShaderNodeMath')
    subtract2.operation = 'SUBTRACT'
    subtract2.inputs[0].default_value = 1.0

    # brightness = max(0, 1 - distance / spot_width)
    divide = nodes.new('ShaderNodeMath')
    divide.operation = 'DIVIDE'
    divide.inputs[1].default_value = props.spot_width # spot_width

    subtract3 = nodes.new('ShaderNodeMath')
    subtract3.operation = 'SUBTRACT'
    subtract3.inputs[0].default_value = 1.0

    maximum = nodes.new('ShaderNodeMath')
    maximum.operation = 'MAXIMUM'
    maximum.inputs[1].default_value = 0.0

    multiply = nodes.new('ShaderNodeMath')
    multiply.operation = 'MULTIPLY'
    multiply.inputs[1].default_value = props.spot_strength
 
    add = nodes.new('ShaderNodeMath')
    add.operation = 'ADD'
    add.inputs[1].default_value = 0.1

    emission = nodes.new('ShaderNodeEmission')
    output = nodes.new('ShaderNodeOutputMaterial')
    emission.inputs['Color'].default_value = (r, g, b, 0.1)


    anim_speed = props.anim_speed 

    driver = spot_pos.outputs[0].driver_add('default_value')
    driver.driver.expression = f"(frame * {anim_speed}) % 1.0"
 
    links.new(attr.outputs['Fac'], subtract.inputs[0]) 
    links.new(spot_pos.outputs['Value'], add_phase.inputs[0])
    links.new(phase.outputs['Fac'], add_phase.inputs[1])
    links.new(add_phase.outputs['Value'], modulo.inputs[0])
    links.new(modulo.outputs['Value'], subtract.inputs[1])
    links.new(subtract.outputs['Value'], absolute.inputs[0])
    links.new(absolute.outputs['Value'], minimum.inputs[0])
    links.new(absolute.outputs['Value'], subtract2.inputs[1])
    links.new(subtract2.outputs['Value'], minimum.inputs[1])
    links.new(minimum.outputs['Value'], divide.inputs[0])
    links.new(divide.outputs['Value'], subtract3.inputs[1])
    links.new(subtract3.outputs['Value'], maximum.inputs[0])
    links.new(maximum.outputs['Value'], multiply.inputs[0])
    links.new(multiply.outputs['Value'], add.inputs[0])
    links.new(add.outputs['Value'], emission.inputs['Strength'])
    links.new(emission.outputs['Emission'], output.inputs['Surface'])

    mat.diffuse_color = (r, g, b, 1.0)
    return mat

def arc_length(points):
    diffs = np.diff(points, axis=0)
    norms = np.linalg.norm(diffs, axis=1)
    lengths= np.concatenate([[0.0], np.cumsum(norms)])
    return lengths

def gen_field_lines_viz(context):
    n = len([c for c in bpy.data.collections if c.name.startswith('run_')])
    streamline_collection = bpy.data.collections.new(f'run_{n}')
    bpy.context.scene.collection.children.link(streamline_collection)
    t_mat = 0.0
    t_points = 0.0 
    t0 = time.perf_counter()
    mat = mat_nodes(context, n)
    t_mat += time.perf_counter() - t0
             
    

    x = np.array([p[0] for s in streamlines for p in s])
    y = np.array([p[1] for s in streamlines for p in s])
    z = np.array([p[2] for s in streamlines for p in s])
 
    flat_x_y_z = np.stack([x, y, z], axis=1).flatten()

    t0 = time.perf_counter()

    curve_data = bpy.data.hair_curves.new(f'curves')
    curve_data.add_curves([len(s) for s in streamlines]) 
    arc_attr = curve_data.attributes.new('arc_param', 'FLOAT', 'POINT')
    radius_attr = curve_data.attributes.new('radius', 'FLOAT', 'POINT')
    phase_attr = curve_data.attributes.new('phase', 'FLOAT', 'CURVE') 
             
    flat_phase = np.array([random.random() for s in streamlines])
    total_points = sum(len(s) for s in streamlines)
    flat_radius = np.full(total_points, 0.1)
    curve_data.position_data.foreach_set('vector', flat_x_y_z)
    phase_attr.data.foreach_set('value', flat_phase)
    radius_attr.data.foreach_set('value', flat_radius)
    
    arc_segments = []
    for s in streamlines:
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

    
class VisualizeStreamlines(Operator):
    """Create the curve objects"""
    bl_idname = "tree.visualize_streamlines"
    bl_label = "Visualize Streamlines"

    def execute(self, context):
        n = len([c for c in bpy.data.collections if c.name.startswith('run_')])
        streamline_collection = bpy.data.collections.new(f'run_{n}')
        bpy.context.scene.collection.children.link(streamline_collection)
        alt_min = context.scene.tree_props.alt_min
        alt_step = context.scene.tree_props.alt_step
        alt_max = context.scene.tree_props.alt_max 
        alts = [alt_min] 
        while alts[-1] + alt_step <= alt_max + 1e-6:
            alts.append(alts[-1] + alt_step)
        t_mat = 0.0
        t_points = 0.0
        for i, alt in enumerate(alts):
            t0 = time.perf_counter()
            mat = mat_nodes(context, i)
            t_mat += time.perf_counter() - t0
            alt_collection = bpy.data.collections.new(f'{alts[i]}_km')
            streamline_collection.children.link(alt_collection) 
            
            alt_streams = [s for s in streamlines if len(s) > 0.0 and abs(s[0][2] - alt) < 0.01]

            lats_np = np.array([p[0] for s in alt_streams for p in s])
            lons_np = np.array([p[1] for s in alt_streams for p in s])
            alts_np = np.array([p[2] for s in alt_streams for p in s])

            x, y, z = convert_to_cart(lats_np, lons_np, alts_np)
            flat_x_y_z = np.stack([x, y, z], axis=1).flatten()

            t0 = time.perf_counter()

            curve_data = bpy.data.hair_curves.new(f'alt{alt}_curves')
            curve_data.add_curves([len(s) for s in alt_streams]) 
            arc_attr = curve_data.attributes.new('arc_param', 'FLOAT', 'POINT')
            radius_attr = curve_data.attributes.new('radius', 'FLOAT', 'POINT')
            phase_attr = curve_data.attributes.new('phase', 'FLOAT', 'CURVE') 
             
            flat_phase = np.array([random.random() for s in alt_streams])
            total_points = sum(len(s) for s in alt_streams)
            flat_radius = np.full(total_points, 0.1)
            curve_data.position_data.foreach_set('vector', flat_x_y_z)
            phase_attr.data.foreach_set('value', flat_phase)
            radius_attr.data.foreach_set('value', flat_radius)

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

class TREE_PT_panel(bpy.types.Panel):
    bl_label = "TREE"
    bl_idname = "TREE_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TREE"

    def draw(self, context):
        props = context.scene.tree_props 
        layout = self.layout
        layout.prop(props, "interval_start")
        layout.prop(props, "interval_end")
        layout.prop(props, "step_size")
        layout.operator(ComputeStreamlines.bl_idname)
        layout.operator(VisualizeStreamlines.bl_idname)

class TREE_PT_seeds(bpy.types.Panel):
    bl_label = "Seeds"
    bl_idname = "TREE_PT_seeds"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TREE"
    bl_parent_id = "TREE_PT_panel"
        
    def draw(self, context):
        props = context.scene.tree_props
        layout = self.layout
        layout.prop(props, "seeds_per_level")
        layout.prop(props, "alt_min")
        layout.prop(props, "alt_max") 
        layout.prop(props, "alt_step")
        layout.prop(props, "anim_speed")
        layout.prop(props, "spot_width")
        layout.prop(props, "spot_strength")


def register():
    bpy.utils.register_class(ImportData)
    bpy.utils.register_class(TREEProperties)
    bpy.types.Scene.tree_props = bpy.props.PointerProperty(type=TREEProperties)
    bpy.utils.register_class(ComputeStreamlines)
    bpy.utils.register_class(VisualizeStreamlines)
    bpy.utils.register_class(TREE_PT_panel)
    bpy.utils.register_class(TREE_PT_seeds)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import) 
    bpy.utils.unregister_class(TREE_PT_seeds)
    bpy.utils.unregister_class(TREE_PT_panel)
    bpy.utils.unregister_class(VisualizeStreamlines)
    bpy.utils.unregister_class(ComputeStreamlines)  
    del bpy.types.Scene.tree_props
    bpy.utils.unregister_class(TREEProperties)
    bpy.utils.unregister_class(ImportData)


if __name__ == "__main__":
    register()
    
    
# #76F3E41A - nice wind color
