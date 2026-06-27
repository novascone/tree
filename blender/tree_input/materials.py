
import bpy
import colorsys
import numpy as np

def mat_nodes(context, i, idx):
 
    props = context.scene.tree_field_props[idx]
    #streamline_collection['interval_start'] = props.interval_start
    #streamline_collection['interval_end'] = props.interval_end
    #streamline_collection['step_size'] = props.step_size
    mat = bpy.data.materials.new(f'mat_{i}')
    mat.use_nodes = True
    hue = (i * 0.618033988749895) % 1
    r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
  
    attr = nodes.new('ShaderNodeAttribute')
    attr.attribute_name = 'arc_param'
    attr.attribute_type = 'GEOMETRY'
    spot_pos = nodes.new('ShaderNodeValue')

    phase = nodes.new('ShaderNodeAttribute')
    phase.attribute_name = 'phase'
    phase.attribute_type = 'GEOMETRY'

    add_phase = nodes.new('ShaderNodeMath')
    add_phase.operation = 'ADD'

    modulo = nodes.new('ShaderNodeMath')
    modulo.operation = 'MODULO'
    modulo.inputs[1].default_value = 1.0
    
    # distance = abs(factor - spot_pos)
    subtract = nodes.new('ShaderNodeMath')
    subtract.operation = 'SUBTRACT'

    absolute = nodes.new('ShaderNodeMath')
    absolute.operation = 'ABSOLUTE'

    minimum = nodes.new('ShaderNodeMath')
    minimum.operation = 'MINIMUM'

    subtract2 = nodes.new('ShaderNodeMath')
    subtract2.operation = 'SUBTRACT'
    subtract2.inputs[0].default_value = 1.0

    # brightness = max(0, 1 - distance / spot_width)
    divide = nodes.new('ShaderNodeMath')
    divide.operation = 'DIVIDE'
    divide.inputs[1].default_value = props.spot_width # spot_width

    subtract3 = nodes.new('ShaderNodeMath')
    subtract3.operation = 'SUBTRACT'
    subtract3.inputs[0].default_value = 1.0

    maximum = nodes.new('ShaderNodeMath')
    maximum.operation = 'MAXIMUM'
    maximum.inputs[1].default_value = 0.0

    multiply = nodes.new('ShaderNodeMath')
    multiply.operation = 'MULTIPLY'
    multiply.inputs[1].default_value = props.spot_strength
 
    add = nodes.new('ShaderNodeMath')
    add.operation = 'ADD'
    add.inputs[1].default_value = 0.1

    speed_attr = nodes.new('ShaderNodeAttribute')
    speed_attr.attribute_name = 'speed'
    speed_attr.attribute_type = 'GEOMETRY'

    color_ramp = nodes.new('ShaderNodeValToRGB')
    if props.color_mode == 'BLUE_RED':
        color_ramp.color_ramp.elements[0].position = 0.0
        color_ramp.color_ramp.elements[0].color = (0, 0, 1, 1)
        color_ramp.color_ramp.elements[1].position = 1.0
        color_ramp.color_ramp.elements[1].color = (1, 0, 0, 1)
    elif props.color_mode == 'VIRIDIS':
        color_ramp.color_ramp.elements[0].position = 0.0
        color_ramp.color_ramp.elements[0].color = (0.267, 0.004, 0.329, 1)
        color_ramp.color_ramp.elements[1].color = (0.992, 0.906, 0.145, 1)
        e1 = color_ramp.color_ramp.elements.new(0.25)
        e1.color = (0.192, 0.408, 0.557, 1)
        e2 = color_ramp.color_ramp.elements.new(0.5)
        e2.color = (0.208, 0.718, 0.475, 1)
        e3 = color_ramp.color_ramp.elements.new(0.75)
        e3.color = (0.565, 0.843, 0.263, 1) 
        
    emission = nodes.new('ShaderNodeEmission')
    output = nodes.new('ShaderNodeOutputMaterial')
    emission.inputs['Color'].default_value = (r, g, b, 0.1)

    anim_speed = props.anim_speed 

    driver = spot_pos.outputs[0].driver_add('default_value')
    driver.driver.expression = f"(frame * {anim_speed}) % 1.0"
 
    links.new(attr.outputs['Fac'], subtract.inputs[0]) 
    links.new(spot_pos.outputs['Value'], add_phase.inputs[0])
    links.new(phase.outputs['Fac'], add_phase.inputs[1])
    links.new(add_phase.outputs['Value'], modulo.inputs[0])
    links.new(modulo.outputs['Value'], subtract.inputs[1])
    links.new(subtract.outputs['Value'], absolute.inputs[0])
    links.new(absolute.outputs['Value'], minimum.inputs[0])
    links.new(absolute.outputs['Value'], subtract2.inputs[1])
    links.new(subtract2.outputs['Value'], minimum.inputs[1])
    links.new(minimum.outputs['Value'], divide.inputs[0])
    links.new(divide.outputs['Value'], subtract3.inputs[1])
    links.new(subtract3.outputs['Value'], maximum.inputs[0])
    links.new(maximum.outputs['Value'], multiply.inputs[0])
    links.new(multiply.outputs['Value'], add.inputs[0])
    links.new(add.outputs['Value'], emission.inputs['Strength'])
    links.new(speed_attr.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], emission.inputs['Color'])
    links.new(emission.outputs['Emission'], output.inputs['Surface'])

    mat.diffuse_color = (r, g, b, 1.0)
    return mat

def sca_mat_nodes(context, idx):
    props = context.scene.tree_field_props[idx]
    mat = bpy.data.materials.new(f'mat')
    mat.use_nodes = True  
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    radiance = nodes.new('ShaderNodeAttribute')
    radiance.attribute_name = 'radiance'
    radiance.attribute_type = 'GEOMETRY'

    color_ramp = nodes.new('ShaderNodeValToRGB') 
    color_ramp.color_ramp.elements[0].position = 0.0
    color_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    color_ramp.color_ramp.elements[1].position = 1.0
    color_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)

    transparent = nodes.new('ShaderNodeBsdfTransparent')
    mix = nodes.new('ShaderNodeMixShader')
    mix.inputs['Fac'].default_value = props.opacity


    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Strength'].default_value = props.strength
    output = nodes.new('ShaderNodeOutputMaterial')

    links.new(radiance.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], emission.inputs['Color'])
    links.new(transparent.outputs['BSDF'], mix.inputs[1])
    links.new(emission.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], output.inputs['Surface'])
    mat.blend_method = 'BLEND'

    return mat
    
