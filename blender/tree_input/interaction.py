

from .materials import texture_mat_nodes
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
texture_path = None
read = None
streamlines = {} 
tree_config = None
field_names = []
_field_classes = []
_field_operators = []


def read_data(input_file):

    global geometry, texture_path, read, tree_config, field_names
    with open(input_file) as f:
        tokens = lex(f)
        
    root = parse(tokens) 
    validate(root)  
    config = convert(root) 
    tree_config = translate(config) 
    geometry = tree_core.build_mesh(tree_config.geometry)
    texture_path = config.geometry.texture
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
            if texture_path:
                mat = texture_mat_nodes(texture_path)
                obj.data.materials.append(mat)
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
        if tree_config.fields[idx].grid_type == "structured" or tree_config.fields[idx].type == "vector":
            seeds_head, seeds_body = layout.panel(f"seeds_{idx}", default_closed=True)
            seeds_head.label(text="Seeds")
            if seeds_body:
                vector_seeds_head, vector_seeds_body = seeds_body.panel(f"vector_seeds_{idx}", default_closed=True)
                vector_seeds_head.label(text="Vector Seeds")
                scalar_seeds_head, scalar_seeds_body = seeds_body.panel(f"scalar_seeds_{idx}", default_closed=True)
                scalar_seeds_head.label(text="Scalar Seeds")
                if vector_seeds_body:
                    vector_seeds_body.prop(props, "vec_seeding_mode")
                    vector_seeds_body.prop(props, "vec_alt_min")
                    vector_seeds_body.prop(props, "vec_alt_max") 
                    if props.vec_seeding_mode == 'FIBONACCI':
                        vector_seeds_body.prop(props, "seeds_per_level")
                        vector_seeds_body.prop(props, "vec_alt_step")
                    elif props.vec_seeding_mode == 'STRATIFIED':
                        vector_seeds_body.prop(props, "vec_lat_cell")
                        vector_seeds_body.prop(props, "vec_lon_cell")
                        vector_seeds_body.prop(props, "vec_alt_cell")
                if scalar_seeds_body:
                    scalar_seeds_body.prop(props, "sca_seeding_mode")
                    scalar_seeds_body.prop(props, "sca_alt_min")
                    scalar_seeds_body.prop(props, "sca_alt_max") 
                    if props.sca_seeding_mode == 'FIBONACCI':
                        scalar_seeds_body.prop(props, "seeds_per_level")
                        scalar_seeds_body.prop(props, "sca_alt_step")
                    elif props.sca_seeding_mode == 'STRATIFIED':
                        scalar_seeds_body.prop(props, "sca_lat_cell")
                        scalar_seeds_body.prop(props, "sca_lon_cell")
                        scalar_seeds_body.prop(props, "sca_alt_cell")
        if tree_config.fields[idx].type == "vector":
            vector_viz_head, vector_viz_body = layout.panel(f"viz_{idx}", default_closed=True)
            vector_viz_head.label(text="Vector Visualiation")
            if vector_viz_body:
                streamline_head, streamline_body = vector_viz_body.panel(f"streamline_{idx}", default_closed=True)
                streamline_head.label(text="Streamline")
                if streamline_body:
                    compute_head, compute_body = streamline_body.panel(f"compute_{idx}", default_closed=True)
                    compute_head.label(text="Compute")
                    if compute_body:
                        compute_body.prop(props, "interval_start")
                        compute_body.prop(props, "interval_end")
                        compute_body.prop(props, "step_size")
                        compute_body.operator(f'tree.compute_{idx}')
                    visualize_head, visualize_body = streamline_body.panel(f"visualize_{idx}", default_closed=True)
                    visualize_head.label(text="Visualize")
                    if visualize_body:
                        visualize_body.prop(props, "color_mode")
                        visualize_body.prop(props, "anim_speed")
                        visualize_body.prop(props, "spot_width")
                        visualize_body.prop(props, "spot_strength") 
                        visualize_body.operator(f'tree.visualize_vector_{idx}')
                scalar_head, scalar_body = vector_viz_body.panel(f"scalar_{idx}", default_closed=True)
                scalar_head.label(text="Scalar")
                if scalar_body:
                    scalar_body.prop(props, "threshold") 
                    scalar_body.prop(props, "point_radius")
                    scalar_body.operator(f'tree.point_cloud_field_{idx}')
        elif tree_config.fields[idx].type == "scalar":
            scalar_viz_head, scalar_viz_body = layout.panel(f"sca_{idx}", default_closed=True)
            scalar_viz_head.label(text="Scalar Visualiation")
            if scalar_viz_body:
                scalar_viz_body.prop(props, "opacity")
                scalar_viz_body.prop(props, "strength")
                scalar_viz_body.prop(props, "point_radius")
                scalar_viz_body.prop(props, "displacement")
                if props.displacement:
                    scalar_viz_body.prop(props, "displacement_scale")
                scalar_viz_body.operator(f'tree.visualize_scalar_{idx}')

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
    threshold: FloatProperty(name="Threshold", default=1.0)
    alt_min_val: FloatProperty(name="Minimum Altitude", default=10000.0)
    alt_max_val: FloatProperty(name="Maximum Altitude", default=18000.0)
    color_mode: EnumProperty(
        name="Color Mode",
        items=[
            ('BLUE_RED', "Blue Red", ""),
            ('VIRIDIS', "Viridis", ""),
        ],
        default='BLUE_RED'
    )
    vec_seeding_mode: EnumProperty(
            name="Seeding Mode",
            items=[
                ('STRATIFIED', "Stratified Random", ""),
                ('FIBONACCI', "Fibonacci Sphere", ""),
                            ],
            default='STRATIFIED'
        )
    sca_seeding_mode: EnumProperty(
            name="Seeding Mode",
            items=[
                ('STRATIFIED', "Stratified Random", ""),
                ('FIBONACCI', "Fibonacci Sphere", ""),
                            ],
            default='STRATIFIED'
        )
    seeds_per_level: IntProperty(name="Seeds Per Level", default=50, min=1)
    coordinate_system: StringProperty(name="Coordinate System")
    vec_alt_min: FloatProperty(name="Alt Min ", default=12000.0)
    sca_alt_min: FloatProperty(name="Alt Min ", default=12000.0)
    vec_alt_max: FloatProperty(name="Alt Max ", default=12000.0)
    sca_alt_max: FloatProperty(name="Alt Max ", default=12000.0)
    vec_alt_step: FloatProperty(name="Alt Step ", default=1000.0, min=0.1)
    sca_alt_step: FloatProperty(name="Alt Step ", default=1000.0, min=0.1)
    vec_lat_cell: FloatProperty(name="Lat Cell (m)", default=100000.0, min=0.1)
    sca_lat_cell: FloatProperty(name="Lat Cell (m)", default=100000.0, min=0.1)
    vec_lon_cell: FloatProperty(name="Lon Cell (m)", default=100000.0, min=0.1)
    sca_lon_cell: FloatProperty(name="Lon Cell (m)", default=100000.0, min=0.1)
    vec_alt_cell: FloatProperty(name="Alt Cell ", default=100000.0, min=0.1)
    sca_alt_cell: FloatProperty(name="Alt Cell ", default=100001.0, min=0.1)
    opacity: FloatProperty(name="Opacity", default=0.05)
    strength: FloatProperty(name="Strength", default=0.3)
    point_radius: FloatProperty(name="Point Radius (m)", default=0.001)
    scalar_min: FloatProperty(name="Scalar Min", default=-1000.0)
    scalar_max: FloatProperty(name="Scalar Max", default=1000.0)
    displacement: BoolProperty(name="Displacement", default=False)
    displacement_scale: FloatProperty(name="Displacement Scale (m)", default=0.005)
    show_seeds: BoolProperty(name="Seeds", default=False)
    show_viz: BoolProperty(name="Visualization", default=False)

class TREE_PT_panel(bpy.types.Panel):
    bl_label = "TREE"
    bl_idname = "TREE_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TREE"

    def draw(self, context): pass
