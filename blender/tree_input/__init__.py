
from . import interaction
from . import operators

import bpy

def register():
    bpy.utils.register_class(interaction.ImportData)
    bpy.utils.register_class(interaction.FieldProperties)
    bpy.types.Scene.tree_field_props = bpy.props.CollectionProperty(type=interaction.FieldProperties)
    bpy.utils.register_class(interaction.TREE_PT_panel) 
    bpy.types.TOPBAR_MT_file_import.append(interaction.menu_func_import)

def unregister():
    interaction.read = None
    interaction.streamlines = {}
    interaction.tree_config = None
    interaction.geometry = None
    bpy.types.TOPBAR_MT_file_import.remove(interaction.menu_func_import) 
    interaction.unregister_field_classes()
    bpy.utils.unregister_class(interaction.TREE_PT_panel)
    operators.unregister_field_operators() 
    del bpy.types.Scene.tree_field_props
    bpy.utils.unregister_class(interaction.FieldProperties)
    bpy.utils.unregister_class(interaction.ImportData)


if __name__ == "__main__":
    register()
    
    
# #76F3E41A - nice wind color
