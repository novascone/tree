
req_attributes = {
    "sphere" : ["radius", "resolution"],
    "stellarator" : ["source"],
    "vector" : ["source", "grid_type", "variables", "coordinates"],
    "scalar" : ["source", "grid_type"],
    "vec_render" : ["colormap", "line_type", "seed_count", "seed_distribution"],
    "scalar_render": ["colormap"],
}

def validate(block, parent = None):
    block.attributes = {k.lower(): v.lower() if k != "source" else v for k, v in block.attributes.items()}
    for child in block.children: 
        validate(child, block) 
    if (parent and parent.name != "root"):
        if parent.attributes.get("type") == "vector":
            for attribute in req_attributes["vec_render"]:
                if attribute not in block.attributes:
                   raise ValueError(f"{attribute} not in attributes of {block.name}") 
        elif parent.attributes.get("type") == "scalar":
            for attribute in req_attributes["scalar_render"]:
                if attribute not in block.attributes:
                    raise ValueError(f"{attribute} not in attributes of {block.name}")  
        else:
            if "type" not in block.attributes:
               raise ValueError(f"{block.name} has no type") 
            if block.attributes["type"] not in req_attributes:
               raise ValueError(f"{block.attributes["type"]} not recognized") 
            for attribute in req_attributes[block.attributes["type"]]:
                if attribute not in block.attributes:
                    raise ValueError(f"{attribute} not in attributes of {block.name}")  
