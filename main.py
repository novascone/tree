
import sys
sys.path.insert(0, 'build')
import tree_core
from blender.parser.lex import lex 
from blender.parser.parse import parse 
from blender.parser.validate import validate  
from blender.parser.convert import convert 
from blender.parser.translate import translate 
#import blender.mesh

def print_tree(blocks):
    for child in blocks.children:
        print(child.name)
        print(child.attributes)
        print_tree(child)


if __name__ == "__main__":

    input_file:str = sys.argv[1]
     
    with open(input_file) as f:
        tokens = lex(f)
    
    root = parse(tokens)
    
    try:
        validate(root)
    except ValueError as e:
        print(e)
        sys.exit(1)

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
    print(f"Coords size {len(read.coords)}")
    print(f"Values size {len(read.values)}")
    print(f"Coord array 0 size {len(read.coords[0])}")
    print(f"Coord array 1 size {len(read.coords[1])}")
    print(f"Coord array 2 size {len(read.coords[2])}")
    print(f"Value array size {len(read.values)}")
    print(f"Values 0 size {len(read.values[0])}")

    seeds = [[0.0, 0.0, 86], [30.0, 90.0, 86.0]]
        
    streamline_set = tree_core.driveField(read, seeds, 0.0, 1.0, 0.1)
    
    for i in range(len(streamline_set)):
        for j in range(len(streamline_set[i])):
            print(streamline_set[i][j])
        
    #blender_mesh = blender.mesh.build_mesh(geometry)
    #test
    

