
import bpy
from bpy import context

scene = context.scene

cursor = scene.cursor.location

obj = context.active_object

obj_new = obj.copy()

scene.collection.objects.lin(obj_new)

obj_new.location = cursor


