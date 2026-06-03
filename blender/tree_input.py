
from . import tree_core
from .parser.lex import lex
from .parser.parse import parse 
from .parser.validate import validate  
from .parser.convert import convert 
from .parser.translate import translate 
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




class VisualizeStreamlines(Operator):
    """Create the curve objects"""
    bl_idname = "tree.visualize_streamlines"
    bl_label = "Visualize Streamlines"

    def execute(self, context):
        n = len([c for c in bpy.data.collections if c.name.startswith('run_')])
        streamline_collection = bpy.data.collections.new(f'run_{n}')
        props = context.scene.tree_props
        streamline_collection['interval_start'] = props.interval_start
        streamline_collection['interval_end'] = props.interval_end
        streamline_collection['step_size'] = props.step_size
        mat = bpy.data.materials.new(f'run_{n}')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        emission = nodes.new('ShaderNodeEmission')
        output = nodes.new('ShaderNodeOutputMaterial')
        hue = (n * 0.618033988749895) % 1
        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
        emission.inputs['Color'].default_value = (r, g, b, 1.0)
        emission.inputs['Strength'].default_value = 2.0
        links.new(emission.outputs['Emission'], output.inputs['Surface'])
        mat.diffuse_color = (r, g, b, 1.0)
        bpy.context.scene.collection.children.link(streamline_collection)
        for i, streamline in enumerate(streamlines):
            curve_data = bpy.data.curves.new(f'streamline_{i}', type='CURVE')
            curve_data.dimensions = '3D'
            curve_data.bevel_depth = 0.001
            curve_data.bevel_resolution = 0
            spline = curve_data.splines.new('POLY')
            spline.points.add(len(streamline) -1)
            for j, point in enumerate(streamline):
                x, y, z = convert_to_cart(point[0], point[1], point[2])
                spline.points[j].co = (x, y, z, 1.0)
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
    
    
    
