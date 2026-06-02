
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

class VecRenderConfig:
    colormap:str
    line_type:str
    seed_count:int
    seed_distribution:str

    def __init__(self):
        self.colormap = None
        self.line_type = None
        self.seed_count = None
        self.seed_distribution = None

class ScalarRenderConfig:
    colormap:str

    def __init__(self):
        self.colormap = None

        
class FieldConfig:
    name:str
    type:str
    source:str
    grid_type:str
    render: VecRenderConfig | ScalarRenderConfig
    variables:str | None
    coordinates:str | None 

    def __init__(self):
        self.name = None
        self.type = None
        self.source = None
        self.grid_type = None
        self.render = None 
        self.variables = None
        self.coordinates = None

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
            if valid_tree.attributes["type"] == "vector":
                field.render = VecRenderConfig()
                for child in valid_tree.children:
                    if child.name == "render":
                        field.render.line_type = cast(child.attributes["line_type"])
                        field.render.colormap = cast(child.attributes["colormap"])
                        field.render.seed_count = cast(child.attributes["seed_count"])
                        field.render.seed_distribution = cast(child.attributes["seed_distribution"])
                field.variables = cast(valid_tree.attributes["variables"])
                field.coordinates = cast(valid_tree.attributes["coordinates"])
            if valid_tree.attributes["type"] == "scalar":
                field.render = ScalarRenderConfig()
                for child in valid_tree.children:
                    if child.name == "render":
                        field.render.colormap = cast(child.attributes["colormap"])  
            TREE_Config.fields.append(field) 
   
    return TREE_Config

def convert(valid_tree) -> TREEConfig:
    TREE_Config = TREEConfig()
    return traverse(TREE_Config, valid_tree)
    

    




