
bl_info = {
	"name": "EP Operator",
	"description": "Animate the change electrical activity on the surface of a heart mesh."
	"author": "Tommy Truong, Jonathan Chiu",
	"version": (1,0),
	"category": "object",
	"blender":(2, 77, 0)
}

import bpy
import numpy as np
import time

class EPAnimation(bpy.types.Operator):
	"""
	A HexBlender operator class that takes in file input and animates a VCG
	based on the coordinates specified in the file.
	"""
	bl_idname = "object.ep_animation"
	bl_label = "EP Animation"
	bl_options = {'REGISTER', 'UNDO'}

    # Arbitrary names
    VC_NAME = 'MyVertexColorLayer'                      # Vertex Color Layer
    KS_NAME = 'MyNewKeyingSet'                          # Keying Set
    SURFACE = 'Surface'
    MATERIAL = 'MyMaterial'
    ATTRIBUTE = 'Attribute'
    EMISSION = 'Emission'
    OUTPUT = 'Material Output'

    # Time constants
    FRAME_NUM = 10                                      # Time between frames
    TIME = 0                                            # Times in colormap
    KEYFRAMES = 1

    # Blender constants
    scn = bpy.context.scene                             # Active scene
    obj = bpy.context.active_object                     # Active object
    mesh = obj.data                                     # Active object's mesh

    # Filepaths
    FILEPATH = '/Users/cmrg/Desktop/500ms.npy'

    # Read in numpy array containing colormap
    print('Loading input file ... One moment ...')
    vsoln_colormap = np.load(FILEPATH)

    # Enable Cycles
    print('Initiating Cycles ...')
    if not scn.render.engine == 'CYCLES':
        scn.render.engine = 'CYCLES'

    # Check for proper vertex color layer
    if VC_NAME not in mesh.vertex_colors:
        print('Deleting old vertex color layers ...')
        for i in range(0, len(mesh.vertex_colors)):
            bpy.ops.mesh.vertex_color_remove()

        print('Creating new vertex color layer ...')
        # Create a new vertex color layer
        mesh.vertex_colors.new(VC_NAME)

    else:
        print(VC_NAME, 'exists!')

    # Check for proper material
    if MATERIAL not in mesh.materials:

        print('Deleting old material slots ...')
        # Delete all material slots
        for i in range(len(mesh.materials)):
            bpy.ops.object.material_slot_remove()

        print('Deleting old materials ...')
        for material in bpy.data.materials:
            material.user_clear()
            bpy.data.materials.remove(material)

        print('Adding new materials ...')
        # Make a new material
        material = bpy.data.materials.new(name=MATERIAL)

        # Append material to the mesh
        mesh.materials.append(material)

        # Enable nodes to display vertex color layer
        material.use_nodes = True
    else:
        print(MATERIAL, 'exists!')

    # Check for proper nodes
    material = bpy.context.object.active_material
    nodes = material.node_tree.nodes
    if OUTPUT and EMISSION and ATTRIBUTE not in nodes:
        # Remove old nodes
        print('Removing old nodes ...')
        for node in nodes:
            nodes.remove(node)

        print('Adding output node...')
        # ShaderNodeOutputMaterial node outputs the combination of appended nodes
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = -100,400

        print('Adding emission node...')
        # ShaderNodeEmission node illuminates the material of the object
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = -300,400

        print('Adding attribute node...')
        # ShaderNodeAttribute colors the object's material with the vertex color layer
        color = nodes.new(type='ShaderNodeAttribute')
        color.location = -500,400

        # Attach the active vertex color layer to the Attribute node
        nodes["Attribute"].attribute_name = VC_NAME

        # Link the attribute node to the emission then to the output node
        print('Linking nodes')
        links = material.node_tree.links
        link_color_emission = links.new(color.outputs[0], emission.inputs[0])
        link_emisison_output = links.new(emission.outputs[0], output.inputs[0])
    else:
        print(OUTPUT, EMISSION, ATTRIBUTE, 'nodes exist!')

    # Select the current vertex color layer
    vertex_color_layer = mesh.vertex_colors[VC_NAME]

    # Map vertex color layer vertices to the global vertices
    reducedMap = np.zeros(len(vertex_color_layer.data),dtype='int')

    # Create a mapping between the local (for vertex colors) and global vertices
    print("Mapping local to global vertices ...")
    local_vertex = 0
    for poly in mesh.polygons:
      for global_vertex in poly.vertices:
        reducedMap[local_vertex] = global_vertex
        local_vertex += 1

    print("Creating vertex group dict ...")
    # Create dictionary for each vertex: (vertex, list of vertex groups)
    vgroup_names = {vgroup.index: vgroup.name for vgroup in obj.vertex_groups}

    # create dictionary of vertex group assignments per vertex
    vgroups = {v.index: [vgroup_names[g.group] for g in v.groups] for v in mesh.vertices}

    # Check for proper keying set
    if KS_NAME not in scn.keying_sets:
        print('Deleting old keying sets ... ')
        for i in range(0, len(scn.keying_sets)):
            bpy.ops.anim.keying_set_remove()

        print("Creating new keying set ...")
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
        print("Filling keying set ... One moment ...")
        for local_vertex in range(0, total_vertices):

            # Only add surface local vertices to the keying set
            if SURFACE in vgroups[reducedMap[local_vertex]]:
                # 'vertex_colors[VC_NAME].data[local_vertex].color'
                data_path = "vertex_colors[\"%s\"].data[%s].color" %(VC_NAME, local_vertex)

                # Add data path to active keying set
                keying_set.paths.add(mesh, data_path)
                print("Data path added for vertex: " + str(local_vertex))
    else:
        print(KS_NAME, 'exists!')

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
        #bpy.ops.anim.keyframe_insert()

        # Update increments
        FRAME_NUM += 10
        TIME += 10

    # End time
    end = time.clock()
    print("Stopped at: " + str(end))
    print("Total time: " + str(end - start))
    print('Finished\n')

    bpy.ops.object.mode_set(mode='VERTEX_PAINT')


#TODO
def register():
	"""
	Register the operator class. Execute by searching for "VCG Animation" in
	3D viewport or calling "vcg_animation()" on an object.
	"""
	bpy.utils.register_class(EPAnimation)

#TODO
def unregister():
	"""
	Remove the operator class from Blender.
	"""
	bpy.utils.unregister_class(EPAnimation)

#TODO (testing only): allows script to be run directly in text editor to test changes
if __name__ == "__main__":

	#register the python plugin when script is run
	register()

	#test call: run "execute" by calling the name defined in bl_idname
	bpy.ops.object.ep_animation()
