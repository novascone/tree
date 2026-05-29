
import tree_core
import os

def translate(TREE_input) -> tree_core.TREEConfig:

    TREEBinds = tree_core.TREEConfig()
    TREEBinds.geometry.name = TREE_input.geometry.name
    TREEBinds.geometry.type = TREE_input.geometry.type
    TREEBinds.geometry.source = os.path.expanduser(TREE_input.geometry.source) if TREE_input.geometry.source is not None else "" 
    TREEBinds.geometry.parameters = dict(TREE_input.geometry.parameters) 

    for field in TREE_input.fields:
        fieldBind = tree_core.FieldConfig()
        fieldBind.name = field.name
        fieldBind.type = field.type
        fieldBind.source = os.path.expanduser(field.source)
        fieldBind.grid_type = field.grid_type
        if field.type == "vector": 
            fieldBind.variables = tree_core.StringVector()
            variables = field.variables.split(" ")
            for var in variables:
                fieldBind.variables.append(var) 
            fieldBind.coordinates = tree_core.StringVector()
            coordinates = field.coordinates.split(" ")
            for coord in coordinates:
                fieldBind.coordinates.append(coord)
            fieldBind.vec_render = tree_core.VecRenderConfig()
            fieldBind.vec_render.colormap = field.render.colormap
            fieldBind.vec_render.line_type = field.render.line_type
            fieldBind.vec_render.seed_count = field.render.seed_count
            fieldBind.vec_render.seed_distribution = field.render.seed_distribution
        if field.type == "scalar":
            fieldBind.scalar_render = tree_core.ScalarRenderConfig()
            fieldBind.scalar_render.colormap = field.render.colormap
        TREEBinds.fields.append(fieldBind)

    return TREEBinds






