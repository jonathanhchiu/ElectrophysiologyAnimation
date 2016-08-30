bl_info = {
	"name": "Animation Creator",
	"description": "Animates randomly generated RGB vertex values",
	"author": "Tommy Truong, Jonathan Chiu",
	"version": (1,0),
	"category": "object",
	"blender":(2, 77, 0)
}

import bpy
import random

#arbitary constants
VC_NAME = 'MyVertexColorLayer'
KS_NAME = 'MyNewKeyingSet'

#Eval time is responsible for the number of frames per second
eval_time = 10

#Set a fresh environment
#Cycles render
scn = bpy.context.scene
if not scn.render.engine == 'CYCLES':
    scn.render.engine = 'CYCLES'

# selection
"""
if bpy.data.objects.get('Cube'):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects['Cube'].select = True

    # remove it
    bpy.ops.object.delete()

    # add cube
    bpy.ops.mesh.primitive_cube_add()
	"""

#grab the active object and scene
obj = bpy.context.active_object
mesh = obj.data

# create a new vertex color layer for the active object
if not mesh.vertex_colors:
    mesh.vertex_colors.new(VC_NAME)
    print("vertex color made")
else:
    for i in range(0, len(mesh.vertex_colors)):
        bpy.ops.mesh.vertex_color_remove()
    mesh.vertex_colors.new(VC_NAME)

if scn.keying_sets:
    for i in range(0, len(scn.keying_sets)):
        bpy.ops.anim.keying_set_remove()

# add absolute keying sets, automatically becomes the active keying set
bpy.ops.anim.keying_set_add()
keying_set = scn.keying_sets.active 			#grab the active keying set

#rename the keying set
keying_set.bl_label = KS_NAME

#grab total number of vertices and calculate total num of color
total_vertices = len(mesh.vertex_colors[VC_NAME].data)

#loop through each face of the selected object
for vertex in range(0, total_vertices):

    data_path = "vertex_colors[\"%s\"].data[%s].color" %(VC_NAME, vertex)

    #settings that should be keyframed together: id and path
    keying_set.paths.add(mesh, data_path)

#material = obj.material_slots[0].material
for i in range(0, len(obj.material_slots)):
	bpy.ops.object.material_slot_remove()

# Set new material
mat = bpy.data.materials.new(name="Material")

# Assign it to object
if mesh.materials:
    # assign to 1st material slot
    mesh.materials[0] = mat
else:
    # no slots
    mesh.materials.append(mat)

bpy.context.object.active_material.use_nodes = True

# get the nodes
nodes = mat.node_tree.nodes

#output = nodes.get("Material Output")
# clear all nodes to start clean
for node in nodes:
    nodes.remove(node)

# create ShaderNodeOutputMaterial node
node_output = nodes.new(type='ShaderNodeOutputMaterial')
node_output.location = -300,200

# create ShaderNodeMixRGB node
node_emission = nodes.new(type='ShaderNodeEmission')
node_emission.location = -300,400

# create attr2 node
node_attr = nodes.new(type='ShaderNodeAttribute')
node_attr.location = -500,400

#Link Attribute to vertex color layer
nodes["Attribute"].attribute_name = VC_NAME

#Create nodal links
links = mat.node_tree.links
link_attr_emission = links.new(node_attr.outputs[0], node_emission.inputs[0])
link_emisison_output = links.new(node_emission.outputs[0], node_output.inputs[0])

#grab the active object and scene
obj = bpy.context.active_object
mesh = obj.data
vertex_color_layer = mesh.vertex_colors[VC_NAME]

#Make a few random vertex color layers and keyframe them
for i in range(0, 3):

	#Move cursor to next keyframe location before every iteration
    bpy.context.scene.frame_set(frame=eval_time)

    #Color the vertices
    j = 0
    for poly in mesh.polygons:
        for idx in poly.loop_indices:
            rgb = [random.random() for k in range(3)]
            vertex_color_layer.data[j].color = rgb
            j += 1

    #Keyframe current color
    bpy.ops.anim.keyframe_insert()

    #1 keyframe per 10 frames
    eval_time += 10

    # set to vertex paint mode to see the result
    bpy.ops.object.mode_set(mode='VERTEX_PAINT')
