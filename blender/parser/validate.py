
req_attributes = {
    "sphere" : ["radius", "resolution"],
    "stellarator" : ["source"],
    "field" : ["source", "grid_type", "variables", "coordinates", "coordinate_system"], 
}

def validate(block, parent = None):
    block.attributes = {k.lower(): v.lower() if k  not in ("source", "variables", "coordinates") else v for k, v in block.attributes.items()}
    for child in block.children: 
        validate(child, block)
    if parent and parent.name == "Geometry":
        if block.attributes["type"] not in req_attributes:
            raise ValueError(f"{block.attributes["type"]} not recognized")
        for attribute in req_attributes[block.attributes["type"]]:
            if attribute not in block.attributes:
                raise ValueError(f"{attribute} not in attributes of {block.name}")
    elif parent and parent.name == "Fields":
        for attribute in req_attributes["field"]:
            if attribute not in block.attributes:
                raise ValueError(f"{attribute} not in attributes of {block.name}")


