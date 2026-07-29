
from .. import tree_core
import pint
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
        fieldBind.variable_units = tree_core.StringVector() 
        if field.variable_units:
            c_variable_convert = [] 
            variable_units = field.variable_units.split(" ")
            for variable_unit in variable_units:
                fieldBind.variable_units.append(variable_unit)
                c_variable_convert.append(pint.Quantity(1, variable_unit).to_base_units().magnitude)
            fieldBind.variable_convert = c_variable_convert
        fieldBind.coordinates = tree_core.StringVector()
        if field.coordinates: 
            coordinates = field.coordinates.split(" ")
            for coord in coordinates:
                fieldBind.coordinates.append(coord)
        fieldBind.coordinate_units = tree_core.StringVector() 
        if field.coordinate_units:  
            coordinate_units = field.coordinate_units.split(" ")
            c_coordinate_convert = []
            for coord_unit in coordinate_units:
                fieldBind.coordinate_units.append(coord_unit)
                c_coordinate_convert.append(pint.Quantity(1, coord_unit).to_base_units().magnitude) 
            fieldBind.coordinate_convert = c_coordinate_convert
        if field.coord_order:
            fieldBind.coord_order = tree_core.StringVector()
            coord_order = field.coord_order.split(" ")
            for place in coord_order:
                fieldBind.coord_order.append(place)
        if field.sentinel is not None:
            fieldBind.sentinel = field.sentinel
        if field.type == "scalar": 
            if field.altitude is not None:
                fieldBind.altitude = field.altitude
        TREEBinds.fields.append(fieldBind)

    return TREEBinds






