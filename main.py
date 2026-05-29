
import sys
sys.path.insert(0, 'build')
from parser.convert import convert
from parser.lex import *
from parser.parse import *
from parser.validate import *
from parser.convert import *
from parser.translate import *
#import blender.mesh

file:str = sys.argv[1]

def print_tree(blocks):    
    for child in blocks.children:
        print(child.name)
        print(child.attributes)
        print_tree(child)

with open(file) as f:
    tokens = lex(f)

root = parse(tokens)


valid_tree:Block

if validate(root):
    valid_tree = root
    config = convert(valid_tree)
    print("geometry type: ", config.geometry.type)
    tree_config = translate(config)
    print(tree_config.geometry.name)
    print("fields: ")
    for field in tree_config.fields:
        print(field.name)
        print(field.source)

        
    print(tree_config.geometry.parameters)
    geometry = tree_core.build_mesh(tree_config.geometry)
    print("Mesh name: ", geometry.name)
    print("Length of positions: ", len(geometry.positions))
    print("Length of faces: ", len(geometry.faces))
    read = tree_core.Read(tree_config.fields[0])
    seeds = [[0.0, 0.0, 86], [30.0, 90.0, 86.0]]
    
    streamline_set = tree_core.driveField(read, seeds)

    for i in range(len(streamline_set)):
        for j in range(len(streamline_set[i])):
            print(streamline_set[i][j])
    
    #blender_mesh = blender.mesh.build_mesh(geometry)
    

    
    
    






