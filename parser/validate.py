
req_attributes = {
    "sphere" : ["radius", "resolution"],
    "stellarator" : ["source"],
    "vector" : ["source", "grid_type", "variables", "coordinates"],
    "scalar" : ["source", "grid_type"],
    "vec_render" : ["colormap", "line_type", "seed_count", "seed_distribution"],
    "scalar_render": ["colormap"],
}

def validate(block, parent = None) -> bool:
    block.attributes = {k.lower(): v.lower() if k != "source" else v for k, v in block.attributes.items()}
    for child in block.children: 
        if not validate(child, block):
            return False 
    if (parent and parent.name != "root"):
        if parent.attributes.get("type") == "vector":
            for attribute in req_attributes["vec_render"]:
                if attribute not in block.attributes:
                    print(attribute, "Not in attributes of", block.name)
                    return False
        elif parent.attributes.get("type") == "scalar":
            for attribute in req_attributes["scalar_render"]:
                if attribute not in block.attributes:
                    print(attribute, "Not in attributes of", block.name)
                    return False
        else:
            if "type" not in block.attributes:
                print("no type")
                return False
            if block.attributes["type"] not in req_attributes:
                print("Unknown type:", block.attributes["type"])
                return False
            for attribute in req_attributes[block.attributes["type"]]:
                if attribute not in block.attributes:
                    print(attribute, "Not in attributes of ", block.name) 
                    return False 
    return True
