import bpy
import numpy as np
import time

# Arbitrary names
VC_NAME = 'MyVertexColorLayer'                      # Vertex Color Layer
KS_NAME = 'MyNewKeyingSet'                          # Keying Set
SURFACE = 'surface'

# Time constants
FRAME_NUM = 10                                      # Time between frames
TIME = 170                                          # Times in colormap
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
    for i in range(len(mesh.vertex_colors)):
        bpy.ops.mesh.vertex_color_remove()

# Create a new vertex color layer for the active object
mesh.vertex_colors.new(VC_NAME)
color_layer = mesh.vertex_colors[VC_NAME]
total_local_vertices = len(color_layer.data)
print('New vertex color layer created.')



# Delete all other keying sets
if scn.keying_sets:
    print('Deleting old keying sets')
    for i in range(len(scn.keying_sets)):
        bpy.ops.anim.keying_set_remove()

# Create a new keying set
bpy.ops.anim.keying_set_add()
keying_set = scn.keying_sets.active
keying_set.bl_label = KS_NAME                               # Rename keying set
print("New keying set created.")



# Grab the index of the "surface" vertex group
surface_index = 0
for group in obj.vertex_groups:
    if group.name == SURFACE:
        surface_index = group.index

surface_group = [True if surface_index == group.group else False for vertex in mesh.vertices for group in vertex.groups]
print("Vertex group dictionary created.")

# Create a mapping between the local (for vertex colors) and global vertices
vertex_map = [global_vertex for face in mesh.polygons for global_vertex in face.vertices]
print("Mapping created between local and global vertices.")



# Add color attributes to the keying set
for local_vertex in range(total_local_vertices):

    # Check that the vertex is on the surface
    if surface_group[vertex_map[local_vertex]]:
        data_path = "vertex_colors[\"%s\"].data[%s].color" % (VC_NAME, local_vertex)
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
colormap = np.load(FILEPATH)



# Start time
start = time.clock()
print("Started at: " + str(start))

# Add a keyframe per iteration
for frame in range(KEYFRAMES):

    #Move cursor to next keyframe location before every iteration
    bpy.context.scene.frame_set(frame=FRAME_NUM)
    
    # Color the vertices in the surface
    print('Begin coloring.')
    for local_vertex in range(total_local_vertices):

        # Color only the vertices in the surface
        if surface_group[vertex_map[local_vertex]]:
            print('Coloring vertex #: ', local_vertex)
            color_layer.data[local_vertex].color = colormap[TIME, vertex_map[local_vertex]][0:3]

    #Keyframe current color
    print("Inserting keyframe " + str(frame))
    bpy.ops.anim.keyframe_insert()
    
    # Update increments
    FRAME_NUM += 10
    TIME += 10

# End time
end = time.clock()
print("Stopped at: " + str(end) + "seconds")
print("Total time: " + str(end - start) + "seconds")
print('Finished adding ' + str(frame) + "keyframes.")



# set to vertex paint mode to see the result
bpy.ops.object.mode_set(mode='VERTEX_PAINT')


