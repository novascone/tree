
from . import tree_core
from .parser.lex import lex
from .parser.parse import parse 
from .parser.validate import validate  
from .parser.convert import convert 
from .parser.translate import translate
from .mesh import build_mesh
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, FloatProperty, PointerProperty
from bpy.types import Operator
import bpy
import colorsys
import math

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
    interval_end: FloatProperty(name="Interval End", default=3.0)
    step_size: FloatProperty(name="Step Size", default=0.1)


class ComputeStreamlines(Operator):
    """Get the path for the streamline"""
    bl_idname = "tree.compute_streamlines"
    bl_label = "Compute Streamlines" 

    def execute(self, context):
        global streamlines
        props = context.scene.tree_props
        seeds = [[lat, lon, 86.0] for lat in range(0, 31, 6) for lon in range(0, 31, 6)]
        streamlines = tree_core.driveField(read, seeds, props.interval_start, props.interval_end, props.step_size)
        return {'FINISHED'}

def convert_to_cart(lat, lon, alt):
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)
    R = 6371.0
    r = (R + alt) / R
    x = r * math.cos(lat_r) * math.cos(lon_r)
    y = r * math.cos(lat_r) * math.sin(lon_r)
    z = r * math.sin(lat_r)

    return x, y, z


def mat_nodes(context):

    n = len([c for c in bpy.data.collections if c.name.startswith('run_')])
    streamline_collection = bpy.data.collections.new(f'run_{n}')
    props = context.scene.tree_props
    streamline_collection['interval_start'] = props.interval_start
    streamline_collection['interval_end'] = props.interval_end
    streamline_collection['step_size'] = props.step_size
    mat = bpy.data.materials.new(f'run_{n}')
    mat.use_nodes = True
    hue = (n * 0.618033988749895) % 1
    r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
  
    attr = nodes.new('ShaderNodeAttribute')
    attr.attribute_name = 'arc_param'
    attr.attribute_type = 'GEOMETRY'
    spot_pos = nodes.new('ShaderNodeValue')
    
    # distance = abs(factor - spot_pos)
    subtract = nodes.new('ShaderNodeMath')
    subtract.operation = 'SUBTRACT'
    absolute = nodes.new('ShaderNodeMath')
    absolute.operation = 'ABSOLUTE'

    # brightness = max(0, 1 - distance / spot_width)
    divide = nodes.new('ShaderNodeMath')
    divide.operation = 'DIVIDE'
    divide.inputs[1].default_value = 0.1 # spot_width

    subtract2 = nodes.new('ShaderNodeMath')
    subtract2.operation = 'SUBTRACT'
    subtract2.inputs[0].default_value = 1.0

    maximum = nodes.new('ShaderNodeMath')
    maximum.operation = 'MAXIMUM'
    maximum.inputs[1].default_value = 0.0 

    add = nodes.new('ShaderNodeMath')
    add.operation = 'ADD'
    add.inputs[1].default_value = 0.1

    emission = nodes.new('ShaderNodeEmission')
    output = nodes.new('ShaderNodeOutputMaterial')
    emission.inputs['Color'].default_value = (r, g, b, 0.1)


    anim_speed = 0.01

    driver = spot_pos.outputs[0].driver_add('default_value')
    driver.driver.expression = f"(frame * {anim_speed}) % 1.0"
 
    links.new(attr.outputs['Fac'], subtract.inputs[0])
    links.new(spot_pos.outputs['Value'], subtract.inputs[1])
    links.new(subtract.outputs['Value'], absolute.inputs[0])
    links.new(absolute.outputs['Value'], divide.inputs[0])
    links.new(divide.outputs['Value'], subtract2.inputs[1])
    links.new(subtract2.outputs['Value'], maximum.inputs[0])
    links.new(maximum.outputs['Value'], add.inputs[0])
    links.new(add.outputs['Value'], emission.inputs['Strength'])
    links.new(emission.outputs['Emission'], output.inputs['Surface'])

    mat.diffuse_color = (r, g, b, 1.0)
    bpy.context.scene.collection.children.link(streamline_collection)

    return mat, streamline_collection

def arc_length(cart_points):
    lengths = [0.0]
    for i in range(1, len(cart_points)):
        dx = cart_points[i][0] - cart_points[i-1][0]
        dy = cart_points[i][1] - cart_points[i-1][1]
        dz = cart_points[i][2] - cart_points[i-1][2]
        lengths.append(lengths[-1] + math.sqrt(dx**2 + dy**2 + dz**2))
    return lengths
    

class VisualizeStreamlines(Operator):
    """Create the curve objects"""
    bl_idname = "tree.visualize_streamlines"
    bl_label = "Visualize Streamlines"

    def execute(self, context): 
        mat, streamline_collection = mat_nodes(context)  
        for i, streamline in enumerate(streamlines):
            curve_data = bpy.data.hair_curves.new(f'streamline_{i}')
            curve_data.add_curves([len(streamline)])
            cart_points = [convert_to_cart(p[0], p[1], p[2]) for p in streamline]
            stream_lens = arc_length(cart_points)
            attr = curve_data.attributes.new('arc_param', 'FLOAT', 'POINT')
            radius_attr = curve_data.attributes.new('radius', 'FLOAT', 'POINT')
            for j, point in enumerate(cart_points):
                x, y, z = point
                curve_data.position_data[j].vector = (x, y, z)
                attr.data[j].value = stream_lens[j] / stream_lens[-1] if stream_lens[-1] > 0 else 0.0  
                radius_attr.data[j].value = 0.1
            obj = bpy.data.objects.new(f'streamline{i}', curve_data)
            obj.data.materials.append(mat)
            streamline_collection.objects.link(obj)
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


def register():
    bpy.utils.register_class(ImportData)
    bpy.utils.register_class(TREEProperties)
    bpy.types.Scene.tree_props = bpy.props.PointerProperty(type=TREEProperties)
    bpy.utils.register_class(ComputeStreamlines)
    bpy.utils.register_class(VisualizeStreamlines)
    bpy.utils.register_class(TREE_PT_panel)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import) 
    bpy.utils.unregister_class(TREE_PT_panel)
    bpy.utils.unregister_class(VisualizeStreamlines)
    bpy.utils.unregister_class(ComputeStreamlines)  
    del bpy.types.Scene.tree_props
    bpy.utils.unregister_class(TREEProperties)
    bpy.utils.unregister_class(ImportData)


if __name__ == "__main__":
    register()
    
    
    
