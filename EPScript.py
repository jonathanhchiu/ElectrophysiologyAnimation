import bpy
import numpy as np
import time

# Arbitrary names
VC_NAME = 'MyVertexColorLayer'                      # Vertex Color Layer
KS_NAME = 'MyNewKeyingSet'                          # Keying Set
SURFACE = 'surface'

# Time constants
FRAME_NUM = 10                                      # Time between frames
TIME = 170                                            # Times in colormap
KEYFRAMES = 2

# Blender constants
scn = bpy.context.scene                             # Active scene
obj = bpy.context.active_object                     # Active object 
mesh = obj.data                                     # Active object's mesh

# Filepaths
FILEPATH = '/Users/cmrg/Desktop/500ms.npy'



# Enable cycles rendering engine
if not scn.render.engine == 'CYCLES':
    scn.render.engine = 'CYCLES'
print('Cycles Engine Initiated.')




# Delete existing vertex color layers
if mesh.vertex_colors:
    print('Deleting old vertex color layers.')
    for i in range(0, len(mesh.vertex_colors)):
        bpy.ops.mesh.vertex_color_remove()

# Create a new vertex color layer for the active object
mesh.vertex_colors.new(VC_NAME)
print('New vertex color layer created.')



# Delete all other keying sets
if scn.keying_sets:
    print('Deleting old keying sets')
    for i in range(0, len(scn.keying_sets)):
        bpy.ops.anim.keying_set_remove()

# Create a new keying set
bpy.ops.anim.keying_set_add()
keying_set = scn.keying_sets.active
keying_set.bl_label = KS_NAME                               # Rename keying set
print("New keying set created.")



# Create dictionary for each vertex: (vertex, list of vertex groups)
vgroup_names = {vgroup.index: vgroup.name for vgroup in obj.vertex_groups}

# create dictionary of vertex group assignments per vertex
vgroups = {v.index: [vgroup_names[g.group] for g in v.groups] for v in mesh.vertices}
print("Vertex group dictionary created.")



# Grab the vertex color layer and initialize array with its length
vertex_color_layer = mesh.vertex_colors[VC_NAME]
reducedMap = np.zeros(len(vertex_color_layer.data),dtype='int')

# Create a mapping between the local (for vertex colors) and global vertices
local_vertex = 0
for poly in mesh.polygons:
  for global_vertex in poly.vertices:
    reducedMap[local_vertex] = global_vertex
    local_vertex += 1
print("Mapping created between local and global vertices.")



# Grab total number of local vertices for vertex color layer
total_vertices = len(mesh.vertex_colors[VC_NAME].data)

# Add each local vertex's color attribute to the keying set
for local_vertex in range(0, total_vertices):
    if 'surface' in vgroups[reducedMap[local_vertex]]:
        data_path = "vertex_colors[\"%s\"].data[%s].color" %(VC_NAME, local_vertex)
        keying_set.paths.add(mesh, data_path)
        print("Data path added for vertex: " + str(local_vertex))



# Create a new material and assign it to an object
mat = bpy.data.materials.new(name="Material")
print('Making new material.')

# Assign it to object
if mesh.materials:
    print('Adding material to object.')
    mesh.materials[0] = mat

else:
    print('Append material to object.')
    mesh.materials.append(mat)



# Use nodes to link vertex color layer to material
bpy.context.object.active_material.use_nodes = True
nodes = mat.node_tree.nodes

# Clear all nodes to start clean
print('Removing old nodes.')
for node in nodes:
    nodes.remove(node)

print('Adding nodes.')

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



# Read in numpy array containing colormap
print('Loading input file.')
vsoln_colormap = np.load(FILEPATH)



# Start time
start = time.clock()
print("Started at: " + str(start))

# Add a keyframe per iteration
for i in range(0, KEYFRAMES):

    #Move cursor to next keyframe location before every iteration
    bpy.context.scene.frame_set(frame=FRAME_NUM)
    
    #Color the vertices
    print('Begin coloring')
    local_vertex = 0
    for poly in mesh.polygons:
        for global_vertex in poly.vertices:

            # Only color vertices in the surface
            if SURFACE in vgroups[reducedMap[local_vertex]]:
                print('Coloring vertex #: ', local_vertex)
                vertex_color_layer.data[local_vertex].color = vsoln_colormap[TIME, global_vertex][0:3]
            local_vertex += 1

    #Keyframe current color
    print("inserting keyframe.")
    bpy.ops.anim.keyframe_insert()
    
    # Update increments
    FRAME_NUM += 10
    TIME += 10

# End time
end = time.clock()
print("Stopped at: " + str(end))
print("Total time: " + str(end - start))
print('Finished\n')



# set to vertex paint mode to see the result
bpy.ops.object.mode_set(mode='VERTEX_PAINT')


