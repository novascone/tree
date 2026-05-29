
import bpy

def build_mesh(core_mesh) -> bpy.types.Mesh:
    vertices = [core_mesh.positions[i*3:i*3+3] for i in range(len(core_mesh.positions)//3)]
    faces = [core_mesh.faces[i*4:i*4+4] for i in range(len(core_mesh.faces)//4)]
    mesh = bpy.data.meshes.new(core_mesh.name)
    mesh.from_pydata(vertices, [], faces)
    return mesh


