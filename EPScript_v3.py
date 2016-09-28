import bpy
import numpy as np
import time

# Arbitrary names
VC_NAME = 'MyVertexColorLayer'                      # Vertex Color Layer
KS_NAME = 'MyNewKeyingSet'                          # Keying Set
SURFACE = 'Surface'
MATERIAL = 'MyMaterial'
ATTRIBUTE = 'Attribute'
EMISSION = 'Emission'
OUTPUT = 'Material Output'

# Time constants
FRAME_NUM = 1                                      # Time between frames
TIME = 0                                            # Times in colormap
START = 0
KEYFRAMES = 262

# Time contants for 2nd job
# FRAME_NUM = 263                                      # Time between frames
# TIME = 262                                            # Times in colormap
# START = 262
# KEYFRAMES = 525

# Find the right place to run the job
with open('log1.txt', 'w') as f:
# with open('log2.txt', 'w') as f:

    # Blender constants
    scn = bpy.context.scene                             # Active scene
    obj = bpy.context.active_object                     # Active object
    mesh = obj.data                                     # Active object's mesh

    # Filepaths
    FILEPATH = '/data/tthao/blender/EP/500ms.npy'

    # Read in numpy array containing colormap
    start = time.clock()

    f.write('Loading input file ... One moment ...\n')
    vsoln_colormap = np.load(FILEPATH)
    end = time.clock()
    f.write("Loading input time: " + str(end - start)) + '\n')

    # Enable Cycles
    f.write('Initiating Cycles ...\n')
    if not scn.render.engine == 'CYCLES':
        scn.render.engine = 'CYCLES'

    # Set to CUDA rendering
    f.write('Initiating CUDA rendering ...\n')
    bpy.context.user_preferences.system.compute_device_type = 'CUDA'
    bpy.context.user_preferences.system.compute_device = 'CUDA_0'

    # For the 2nd job
    # bpy.context.user_preferences.system.compute_device = 'CUDA_1'

    # Check for proper vertex color layer
    if VC_NAME not in mesh.vertex_colors:
        f.write('Deleting old vertex color layers ...\n')
        for i in range(0, len(mesh.vertex_colors)):
            bpy.ops.mesh.vertex_color_remove()

        f.write('Creating new vertex color layer ...\n')
        # Create a new vertex color layer
        mesh.vertex_colors.new(VC_NAME)
    else:
        f.write(VC_NAME, 'exists!')

    # Check for proper material
    if MATERIAL not in mesh.materials:

        f.write('Deleting old material slots ...\n')
        # Delete all material slots
        for i in range(len(mesh.materials)):
            bpy.ops.object.material_slot_remove()

        f.write('Deleting old materials ...\n')
        for material in bpy.data.materials:
            material.user_clear()
            bpy.data.materials.remove(material)

        f.write('Adding new materials ...\n')
        # Make a new material
        material = bpy.data.materials.new(name=MATERIAL)

        # Append material to the mesh
        mesh.materials.append(material)

        # Enable nodes to display vertex color layer
        material.use_nodes = True
    else:
        f.write(MATERIAL, 'exists!\n')

# # Check for proper nodes
# material = bpy.context.object.active_material
# nodes = material.node_tree.nodes
# if OUTPUT and EMISSION and ATTRIBUTE not in nodes:
#     # Remove old nodes
#     print('Removing old nodes ...')
#     for node in nodes:
#         nodes.remove(node)
#
#     print('Adding output node...')
#     # ShaderNodeOutputMaterial node outputs the combination of appended nodes
#     output = nodes.new(type='ShaderNodeOutputMaterial')
#     output.location = -100,400
#
#     print('Adding emission node...')
#     # ShaderNodeEmission node illuminates the material of the object
#     emission = nodes.new(type='ShaderNodeEmission')
#     emission.location = -300,400
#
#     print('Adding attribute node...')
#     # ShaderNodeAttribute colors the object's material with the vertex color layer
#     color = nodes.new(type='ShaderNodeAttribute')
#     color.location = -500,400
#
#     # Attach the active vertex color layer to the Attribute node
#     nodes["Attribute"].attribute_name = VC_NAME
#
#     # Link the attribute node to the emission then to the output node
#     print('Linking nodes')
#     links = material.node_tree.links
#     link_color_emission = links.new(color.outputs[0], emission.inputs[0])
#     link_emisison_output = links.new(emission.outputs[0], output.inputs[0])
# else:
#     print(OUTPUT, EMISSION, ATTRIBUTE, 'nodes exist!')

    # Select the current vertex color layer
    vertex_color_layer = mesh.vertex_colors[VC_NAME]

    # Map vertex color layer vertices to the global vertices
    reducedMap = np.zeros(len(vertex_color_layer.data),dtype='int')

    # Create a mapping between the local (for vertex colors) and global vertices
    f.write("Mapping local to global vertices ...\n")
    local_vertex = 0
    for poly in mesh.polygons:
        for global_vertex in poly.vertices:
            reducedMap[local_vertex] = global_vertex
            local_vertex += 1

    f.write("Creating vertex group dict ...\n")
    # Create dictionary for each vertex: (vertex, list of vertex groups)
    vgroup_names = {vgroup.index: vgroup.name for vgroup in obj.vertex_groups}

    # create dictionary of vertex group assignments per vertex
    vgroups = {v.index: [vgroup_names[g.group] for g in v.groups] for v in mesh.vertices}

    # Check for proper keying set
    if KS_NAME not in scn.keying_sets:
        f.write('Deleting old keying sets ... \n')
        for i in range(0, len(scn.keying_sets)):
            bpy.ops.anim.keying_set_remove()

        f.write("Creating new keying set ...\n")
        # Create a new keying set
        bpy.ops.anim.keying_set_add()

        # Set current keying set as active
        keying_set = scn.keying_sets.active

        # Rename keying set
        keying_set.bl_label = KS_NAME

        # Retrieve the total number of local vertices in the color layer
        total_vertices = len(mesh.vertex_colors[VC_NAME].data)

        # Add each local vertex's color attribute to the keying set
        # Add the RGB values of the local vertices to be keyframed
        f.write("Filling keying set ... One moment ...\n")
        # Read in numpy array containing colormap
        start = time.clock()
        for local_vertex in range(0, total_vertices):

            # Only add surface local vertices to the keying set
            if SURFACE in vgroups[reducedMap[local_vertex]]:
                # 'vertex_colors[VC_NAME].data[local_vertex].color'
                data_path = "vertex_colors[\"%s\"].data[%s].color" %(VC_NAME, local_vertex)

                # Add data path to active keying set
                keying_set.paths.add(mesh, data_path)
                f.write("Data path added for vertex: " + str(local_vertex) + '\n')
            else:
                f.write(KS_NAME, 'exists!\n')
        end = time.clock()
        f.write("Keyingset time: " + str(end - start)) + '\n')

    # Start time
    start = time.clock()

    # Add a keyframe per iteration
    for i in range(START, KEYFRAMES):

        #Move cursor to next keyframe location before every iteration
        bpy.context.scene.frame_set(frame=FRAME_NUM)

        #Color the vertices
        f.write('Begin coloring...\n')
        local_vertex = 0
        for poly in mesh.polygons:
            for global_vertex in poly.vertices:
                # Only color vertices in the surface
                if SURFACE in vgroups[reducedMap[local_vertex]]:
                    f.write('Coloring vertex #: ', local_vertex + '\n')
                    vertex_color_layer.data[local_vertex].color = vsoln_colormap[TIME, global_vertex][0:3]
                local_vertex += 1

        #Keyframe current color
        f.write("inserting keyframe...\n")
        bpy.ops.anim.keyframe_insert()

        # Update increments
        FRAME_NUM += 1
        TIME += 1

    # End time
    end = time.clock()
    f.write("Loading input time: " + str(end - start)) + '\n')
    f.write('Finished\n')
