

from .. import tree_core
from ..parser.lex import lex
from ..parser.parse import parse 
from ..parser.validate import validate  
from ..parser.convert import convert 
from ..parser.translate import translate
from ..mesh import build_mesh
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, FloatProperty, IntProperty, EnumProperty, BoolProperty
from bpy.types import Operator
import bpy
import numpy as np

geometry = None
read = None
streamlines = {} 
tree_config = None
field_names = []
_field_classes = []
_field_operators = []


def read_data(input_file):

    global geometry, read, tree_config, field_names
    with open(input_file) as f:
        tokens = lex(f)
        
    root = parse(tokens) 
    validate(root)  
    config = convert(root) 
    tree_config = translate(config) 
    geometry = tree_core.build_mesh(tree_config.geometry)
    read = [tree_core.Read(field) for field in tree_config.fields]
    field_names = [field.name for field in tree_config.fields]
    

class ImportData(Operator, ImportHelper):
    """Import an input .i file"""
    bl_idname = "import.tree_data"
    bl_label = "Import Data"

    filename_ext = ".i"

    filter_glob: StringProperty(default="*.i")

    def execute(self, context):
        from . import operators

        try:
            read_data(self.filepath)
            mesh = build_mesh(geometry)
            obj = bpy.data.objects.new(geometry.name, mesh)
            bpy.context.collection.objects.link(obj)
            register_field_classes()
            operators.register_field_operators()
            scene = context.scene
            scene.tree_field_props.clear()
            for field in tree_config.fields:
                item = scene.tree_field_props.add()
                item.coordinate_system = field.coordinate_system
        except ValueError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        return {'FINISHED'} 


def menu_func_import(self, context):
    self.layout.operator(ImportData.bl_idname, text="Import TREE file")

def draw_factory(idx):
    global field_names, tree_config
    def draw(self, context): 
        props = context.scene.tree_field_props[idx]
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.prop(props, "show_seeds", icon='TRIA_DOWN' if props.show_seeds else 'TRIA_RIGHT', emboss=False)
        if props.show_seeds:
           box.prop(props, "seeding_mode")
           box.prop(props, "alt_min")
           box.prop(props, "alt_max") 
           if props.seeding_mode == 'FIBONACCI':
                box.prop(props, "seeds_per_level")
                box.prop(props, "alt_step")
           elif props.seeding_mode == 'STRATIFIED':
                box.prop(props, "lat_cell")
                box.prop(props, "lon_cell")
                box.prop(props, "alt_cell")
        if tree_config.fields[idx].type == "vector":
            box1 = layout.box()
            row1 = box1.row()
            row1.prop(props, "show_viz", icon='TRIA_DOWN' if props.show_viz else 'TRIA_RIGHT', emboss=False)
            if props.show_viz:
                box1.prop(props, "interval_start")
                box1.prop(props, "interval_end")
                box1.prop(props, "step_size")
                box1.operator(f'tree.compute_{idx}')
                box1.operator(f'tree.visualize_{idx}')
                box1.prop(props, "color_mode")
                box1.prop(props, "anim_speed")
                box1.prop(props, "spot_width")
                box1.prop(props, "spot_strength")
    return draw

def register_field_classes():
    global _field_classes, field_names
    unregister_field_classes()

    for i, field in enumerate(field_names):
        cls = type(f'TREE_PT_field_{i}', (bpy.types.Panel,), {
            'bl_label': field,
            'bl_idname': f'TREE_PT_field_{i}',
            'bl_space_type': 'VIEW_3D',
            'bl_region_type': 'UI',
            'bl_category': 'TREE',
            'bl_parent_id': 'TREE_PT_panel',
            'draw': draw_factory(i),
        })
        bpy.utils.register_class(cls)
        _field_classes.append(cls)



def unregister_field_classes():
    global _field_classes

    for field in _field_classes:
        bpy.utils.unregister_class(field)
    _field_classes.clear()


class FieldProperties(bpy.types.PropertyGroup):
    interval_start: FloatProperty(name="Interval Start", default=0.0)
    interval_end: FloatProperty(name="Interval End", default=10800)
    step_size: FloatProperty(name="Step Size", default=0.1)
    anim_speed: FloatProperty(name="Anim Speed", default=0.01, min=0.001, max=1.0)
    spot_width: FloatProperty(name="Spot Width", default=0.1, min=0.01, max=1.0) 
    spot_strength: FloatProperty(name="Spot Strength", default=1.0)
    color_mode: EnumProperty(
        name="Color Mode",
        items=[
            ('BLUE_RED', "Blue Red", ""),
            ('VIRIDIS', "VIRIDIS", ""),
        ],
        default='BLUE_RED'
    )
    seeding_mode: EnumProperty(
            name="Seeding Mode",
            items=[
                ('FIBONACCI', "Fibonacci Sphere", ""),
                ('STRATIFIED', "Stratified Random", ""),
            ],
            default='FIBONACCI'
        )
    seeds_per_level: IntProperty(name="Seeds Per Level", default=50, min=1)
    coordinate_system: StringProperty(name="Coordinate System")
    alt_min: FloatProperty(name="Alt Min (km)", default=83.0)
    alt_max: FloatProperty(name="Alt Max (km)", default=90.0)
    alt_step: FloatProperty(name="Alt Step (km)", default=1.0, min=0.1)
    lat_cell: FloatProperty(name="Lat Cell (deg)", default=1.0, min=0.1)
    lon_cell: FloatProperty(name="Lon Cell (deg)", default=1.0, min=0.1)
    alt_cell: FloatProperty(name="Alt Cell (km)", default=1.0, min=0.1)  
    show_seeds: BoolProperty(name="Seeds", default=False)
    show_viz: BoolProperty(name="Visualization", default=False)

class TREE_PT_panel(bpy.types.Panel):
    bl_label = "TREE"
    bl_idname = "TREE_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TREE"

    def draw(self, context): pass
