import bpy
import numpy as np
import time

#arbitary constants
VC_NAME = 'MyVertexColorLayer'
KS_NAME = 'MyNewKeyingSet'

#Eval time is amount of frames per keyframe
EVAL_TIME = 10
MS = 170

#Set a fresh environment
#Cycles render
scn = bpy.context.scene
if not scn.render.engine == 'CYCLES':
    scn.render.engine = 'CYCLES'

print('Cycles Engine Initiated')

#grab the active object and scene
obj = bpy.context.active_object
mesh = obj.data

#print('Setting obj & mesh')

# Set to object mode

# create a new vertex color layer for the active object
if not mesh.vertex_colors:
    mesh.vertex_colors.new(VC_NAME)
    print('Creating new vertex color layer')
else:
    print('Deleting old vert color layer')
    for i in range(0, len(mesh.vertex_colors)):
        bpy.ops.mesh.vertex_color_remove()
    print('Creating new vertex color layer')
    mesh.vertex_colors.new(VC_NAME)

if scn.keying_sets:
    print('Deleting old keying sets')
    for i in range(0, len(scn.keying_sets)):
        bpy.ops.anim.keying_set_remove()

# create vertex group lookup dictionary for names
vgroup_names = {vgroup.index: vgroup.name for vgroup in obj.vertex_groups}

# create dictionary of vertex group assignments per vertex
vgroups = {v.index: [vgroup_names[g.group] for g in v.groups] for v in mesh.vertices}

# Select color layer
vertex_color_layer = mesh.vertex_colors[VC_NAME]

reducedMap = np.zeros(len(vertex_color_layer.data),dtype='int')
j=0
for poly in mesh.polygons:
  for idx in poly.vertices:
    reducedMap[j] = idx
    j=j+1

#add absolute keying sets, automatically becomes the active keying set
bpy.ops.anim.keying_set_add()
keying_set = scn.keying_sets.active 			#grab the active keying set

#rename the keying set
keying_set.bl_label = KS_NAME

#grab total number of vertices and calculate total num of color
total_vertices = len(mesh.vertex_colors[VC_NAME].data)

#loop through each face of the selected object
print(total_vertices, 'vertices total')
for vertex in range(0, total_vertices):
	if 'surface' in vgroups[reducedMap[vertex]]:
		print('Datapath: ', vertex)
		data_path = "vertex_colors[\"%s\"].data[%s].color" %(VC_NAME, vertex)
		#settings that should be keyframed together: id and path
		keying_set.paths.add(mesh, data_path)

# Set new material
print('Making new material')
mat = bpy.data.materials.new(name="Material")

# Assign it to object
if mesh.materials:
    print('Add material to obj')
    # assign to 1st material slot
    mesh.materials[0] = mat
else:
    # no slots
    print('Append material to obj')
    mesh.materials.append(mat)

bpy.context.object.active_material.use_nodes = True

print('Grabbing nodes')
# get the nodes
nodes = mat.node_tree.nodes

#output = nodes.get("Material Output")
# clear all nodes to start clean
print('Removing old nodes')
for node in nodes:
    nodes.remove(node)

print('Adding nodes')
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
print('Linking nodes')
links = mat.node_tree.links
link_attr_emission = links.new(node_attr.outputs[0], node_emission.inputs[0])
link_emisison_output = links.new(node_emission.outputs[0], node_output.inputs[0])

# Select color layer
vertex_color_layer = mesh.vertex_colors[VC_NAME]

#print("creating keying set")
#j=0
#for poly in mesh.polygons:
#  for idx in poly.vertices:
#    if 'surface' in vgroups[reducedMap[j]]:
#            print('adding vertex to keying set #: ', j)
#            data_path = "vertex_colors[\"%s\"].data[%s].color" %(VC_NAME, j)
#            #settings that should be keyframed together: id and path
#            keying_set.paths.add(mesh, data_path)
#    j += 1


print('Loading input file')
vsoln_colormap = np.load('/Users/cmrg/Desktop/500ms.npy')
# 150, 160, 170, 180, 190, 200, 210, 220, 230, 240

#start stopwatch
start = time.clock()
print("Starting clock..." + str(start))

for i in range(0, 2):
	#Move cursor to next keyframe location before every iteration
	bpy.context.scene.frame_set(frame=EVAL_TIME)
	
	#Color the vertices
	print('Begin coloring')
	j = 0
	for poly in mesh.polygons:
	    for idx in poly.vertices:
	        if 'surface' in vgroups[reducedMap[j]]:
	            print('Coloring vertex #: ', j)
	            vertex_color_layer.data[j].color = vsoln_colormap[MS,idx][0:3]
	        j += 1

	#Keyframe current color
	print("inserting keyframe")
	bpy.ops.anim.keyframe_insert()
	
	#1 keyframe per 10 frames
	EVAL_TIME += 10
	
	MS += 10

#end stopwatch
end = time.clock()
print("Stopped at: " + str(end))
print(end - start)

print('Finished\n')
# set to vertex paint mode to see the result
bpy.ops.object.mode_set(mode='VERTEX_PAINT')
