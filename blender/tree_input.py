
from . import tree_core
from .parser.lex import lex
from .parser.parse import parse 
from .parser.validate import validate  
from .parser.convert import convert 
from .parser.translate import translate 
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import bpy

geometry = None
read = None

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

def register():
    bpy.utils.register_class(ImportData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
    
    
    
