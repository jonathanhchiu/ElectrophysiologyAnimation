bl_info = {
	"name": "Vertex Color Animation",
	"description": "Generates random vertex colors for a sphere. Uses a mixRGB"
                    "node to animate changes from one vertex color layer to next."
	"author": "Tommy Truong",
	"version": (1,0),
	"category": "object",
	"blender":(2, 77, 0)
}

import bpy
import random

#Cycles render
scn = bpy.context.scene
if not scn.render.engine == 'CYCLES':
    scn.render.engine = 'CYCLES'

# selection
if bpy.data.objects.get('Cube'):
    bpy.data.objects['Cube'].select = True

    # remove it
    bpy.ops.object.delete()

if bpy.data.objects.get('Sphere'):
    obj = bpy.data.objects["Sphere"]
    mesh = obj.data
    if mesh.vertex_colors:
        for i in range(0, len(mesh.vertex_colors)):
            bpy.ops.mesh.vertex_color_remove()

    # remove it
    oldMode = bpy.context.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects['Sphere'].select = True
    bpy.ops.object.delete()

# add uv sphere
bpy.ops.mesh.primitive_uv_sphere_add()

# start in object mode
obj = bpy.data.objects["Sphere"]
print(obj.data)
mesh = obj.data

#check if our mesh already has Vertex Colors, and if not add some... (first we need to make sure it's the active object)
scn.objects.active = obj
obj.select = True

# test color
color1 = (1.0, 0.0, 1.0) #pink
color2 = (0.0, 0.0, 255.0) #blue
color3 = (192.0, 65.0, 65.0) #red
color4 = (0.0, 102.0, 51.0) #green

color_list = [color1, color2, color3, color4]

vcol1 = mesh.vertex_colors.new()
vcol2 = mesh.vertex_colors.new()
vcol3 = mesh.vertex_colors.new()
vcol4 = mesh.vertex_colors.new()

vcol_list = [vcol1, vcol2, vcol3, vcol4]

for vcol in vcol_list:
    #vcol = mesh.vertex_colors.active()
    for poly in mesh.polygons:
        for idx in poly.loop_indices:
            rand = random.randint(0, 3)
            vcol.data[idx].color = color_list[rand]

# set to vertex paint mode to see the result
#bpy.ops.object.mode_set(mode='VERTEX_PAINT')

# Get material
mat = bpy.data.materials.get("Material")
if mat is None:
    # create material
    mat = bpy.data.materials.new(name="Material")

# Assign it to object
if obj.data.materials:
    # assign to 1st material slot
    obj.data.materials[0] = mat
else:
    # no slots
    obj.data.materials.append(mat)

bpy.context.object.active_material.use_nodes = True

# get the material
mat = bpy.data.materials['Material']
# get the nodes
nodes = mat.node_tree.nodes

# get some specific node:
# returns None if the node does not exist
diffuse = nodes.get("Diffuse BSDF")
output = nodes.get("Material Output")
# clear all nodes to start clean
for node in nodes:
    if node is diffuse or output:
        continue
    nodes.remove(node)

# create attr1 node
node_attr1 = nodes.new(type='ShaderNodeAttribute')
#node_attr1.inputs[3].default_value =  "Col" # color
node_attr1.location = -500,500

# create attr2 node
node_attr2 = nodes.new(type='ShaderNodeAttribute')
#node_attr2.inputs[3].default_value =  "Col.001" # color
node_attr2.location = -500,300

# create ShaderNodeMixRGB node
node_mixRGB = nodes.new(type='ShaderNodeMixRGB')
#node_mixRGB.inputs[0].default_value = (0)  # fac
node_mixRGB.location = -300,400

links = mat.node_tree.links
link_attr1_mixRGB = links.new(node_attr1.outputs[0], node_mixRGB.inputs[1])
link_attr2_mixRGB = links.new(node_attr2.outputs[0], node_mixRGB.inputs[2])
link_mixRGB_diffuse = links.new(node_mixRGB.outputs[0], diffuse.inputs[0])

nodes["Attribute"].attribute_name = "Col"
nodes["Attribute.001"].attribute_name = "Col.001"

nodes["Mix"].inputs[0].default_value = 0.0
diffuse.inputs[0].keyframe_insert(data_path="default_value",frame=10)

nodes["Mix"].inputs[0].default_value = 0.25
diffuse.inputs[0].keyframe_insert(data_path="default_value",frame=20)

nodes["Mix"].inputs[0].default_value = 0.50
diffuse.inputs[0].keyframe_insert(data_path="default_value",frame=30)

nodes["Mix"].inputs[0].default_value = 0.75
diffuse.inputs[0].keyframe_insert(data_path="default_value",frame=40)

nodes["Mix"].inputs[0].default_value = 1.00
diffuse.inputs[0].keyframe_insert(data_path="default_value",frame=50)
