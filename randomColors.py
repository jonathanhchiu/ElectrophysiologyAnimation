import bpy
import random

# start in object mode
 
obj = bpy.context.active_object.data
 
color_map_collection = obj.vertex_colors
if len(color_map_collection) == 0:
    color_map_collection.new()
 
"""
let us assume for sake of brevity that there is now 
a vertex color map called  'Col'    
"""
 
color_map = color_map_collection.active

# or you could avoid using the vertex color map name
# color_map = color_map_collection.active  
 
i = 0
for poly in obj.polygons:
    rgb = [random.random() for i in range(3)]
    
    for idx in poly.loop_indices:
        color_map.data[i].color = rgb
        i += 1

# set to vertex paint mode to see the result
bpy.ops.object.mode_set(mode='VERTEX_PAINT')