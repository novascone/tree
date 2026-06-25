
from .. import tree_core
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
        fieldBind.coordinate_system = field.coordinate_system  
        fieldBind.variables = tree_core.StringVector()
        if field.variables:
            variables = field.variables.split(" ")
            for var in variables:
                fieldBind.variables.append(var)
        fieldBind.coordinates = tree_core.StringVector()
        if field.coordinates: 
            coordinates = field.coordinates.split(" ")
            for coord in coordinates:
                fieldBind.coordinates.append(coord) 
        if field.type == "scalar": 
            if field.altitude is not None:
                fieldBind.altitude = field.altitude
        TREEBinds.fields.append(fieldBind)

    return TREEBinds






