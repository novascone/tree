
from . import tree_core
from .parser.lex import lex
from .parser.parse import parse 
from .parser.validate import validate  
from .parser.convert import convert 
from .parser.translate import translate 
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, FloatProperty
from bpy.types import Operator
import bpy

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
    """Tool tip"""
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


class ComputeStreamlines(Operator):
    """Tool tip"""
    bl_idname = "tree.compute_streamlines"
    bl_label = "Compute Streamlines"
 
    interval_start: FloatProperty(name="Interval Start", default=0.0)
    interval_end: FloatProperty(name="Interval End", default=3.0)
    step_size: FloatProperty(name="Step Size", default=0.1)

    def execute(self, context):
        seeds = [[lat, lon, 86.0] for lat in range(0, 31, 6) for lon in range(0, 31, 6)]
        global streamlines
        streamlines = tree_core.driveField(read, seeds, self.interval_start, self.interval_end, self.step_size)
        return {'FINISHED'}


class VisualizeStreamlines(Operator):
    """Tool tip"""
    bl_idname = "tree.visualize_streamlines"
    bl_label = "Visualize Streamlines"

    def execute(self, context):
        for i, streamline in enumerate(streamlines):
            curve_data = bpy.data.curves.new(f'streamline_{i}', type='CURVE')
            curve_data.dimensions = '3D'
            curve_data.bevel_depth = 0.05
            spline = curve_data.splines.new('POLY')
            spline.points.add(len(streamline) -1)
            for j, point in enumerate(streamline):
                spline.points[j].co = (point[0], point[1], point[2], 1.0)
            obj = bpy.data.objects.new(f'streamline{i}', curve_data)
            bpy.context.collection.objects.link(obj)
        return {'FINISHED'}


class TREE_PT_panel(bpy.types.Panel):
    bl_label = "TREE"
    bl_idname = "TREE_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TREE"

    def draw(self, context):
        layout = self.layout
        layout.operator(ComputeStreamlines.bl_idname)
        layout.operator(VisualizeStreamlines.bl_idname)


def register():
    bpy.utils.register_class(ImportData)
    bpy.utils.register_class(ComputeStreamlines)
    bpy.utils.register_class(VisualizeStreamlines)
    bpy.utils.register_class(TREE_PT_panel)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import) 
    bpy.utils.unregister_class(TREE_PT_panel)
    bpy.utils.unregister_class(VisualizeStreamlines)
    bpy.utils.unregister_class(ComputeStreamlines)  
    bpy.utils.unregister_class(ImportData)


if __name__ == "__main__":
    register()
    
    
    
