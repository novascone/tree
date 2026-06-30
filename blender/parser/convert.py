
class GeometryConfig:
    name:str
    type:str
    source:str | None
    parameters:dict

    def __init__(self):
        self.name = None
        self.source = None
        self.type = None
        self.parameters = None
        
class FieldConfig:
    name:str
    type:str
    source:str
    grid_type:str 
    variables:str | None
    coordinates:str | None 
    coordinate_system:str | None
    coord_order:str | None
    altitude:float | None

    def __init__(self):
        self.name = None
        self.type = None
        self.source = None
        self.grid_type = None 
        self.variables = None
        self.coordinates = None
        self.coordinate_system = None
        self.coord_order = None
        self.altitude = None

class TREEConfig:
    geometry: GeometryConfig
    fields: list[FieldConfig]

    def __init__(self):
        self.geometry = None
        self.fields = []

known_geometry = [
    "sphere",
    "stellarator",
]

known_fields = [
    "vector",
    "scalar",
]

known_colormaps = [
    "plasma",
]

def set_geometry_parameters(attributes) -> dict:
    parameters = {}
    for k, v in attributes.items():
        if k not in ("type", "source"):
            parameters[k] = v
    return parameters

def cast(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value

def traverse(TREE_Config, valid_tree, parent = None) -> TREEConfig: 
    for child in valid_tree.children:
        traverse(TREE_Config, child, valid_tree)
    if parent:
        if parent.name == "Geometry":
            geometry = GeometryConfig()
            geometry.name = valid_tree.name
            geometry.type = valid_tree.attributes["type"]
            if "source" in valid_tree.attributes:
                geometry.source = valid_tree.attributes["source"]
            else:
                geometry.source = None
            geometry.parameters = set_geometry_parameters(valid_tree.attributes)
            TREE_Config.geometry = geometry 
        elif parent.name == "Fields":
            field = FieldConfig()
            field.name = valid_tree.name
            field.type = cast(valid_tree.attributes["type"])
            field.grid_type = cast(valid_tree.attributes["grid_type"])
            field.source = cast(valid_tree.attributes["source"]) 
            field.coordinate_system = cast(valid_tree.attributes["coordinate_system"]) 
            field.variables = cast(valid_tree.attributes["variables"])
            field.coordinates = cast(valid_tree.attributes["coordinates"])
            if "coord_order" in valid_tree.attributes:
                field.coord_order = cast(valid_tree.attributes["coord_order"])
            if valid_tree.attributes["type"] == "scalar":
                if "altitude" in valid_tree.attributes:
                    field.altitude = cast(valid_tree.attributes["altitude"])
            TREE_Config.fields.append(field) 
   
    return TREE_Config

def convert(valid_tree) -> TREEConfig:
    TREE_Config = TREEConfig()
    return traverse(TREE_Config, valid_tree)
    

    




