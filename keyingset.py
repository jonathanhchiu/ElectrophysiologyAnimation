import bpy

#arbitary constants
VC_NAME = 'MyVertexColorLayer'
KS_NAME = 'MyNewKeyingSet'
COLOR_VALUE = (0, 1, 2)

def create_keying_set():

	# start in object mode
	bpy.context.scene.objects.active = bpy.data.objects["Cube"]

	#grab the active object and scene
	obj = bpy.context.active_object
	mesh = obj.data
	scene = bpy.context.scene

	# create a new vertex color layer for the active object
	if not mesh.vertex_colors:
		mesh.vertex_colors.new(VC_NAME)
	else:
		for i in range(0, len(mesh.vertex_colors)):
			bpy.ops.mesh.vertex_color_remove()

	# add absolute keying sets, automatically becomes the active keying set
	bpy.ops.anim.keying_set_add()
	keying_set = scene.keying_sets.active 			#grab the active keying set

	#rename the keying set
	keying_set.bl_label = KS_NAME

	#grab total number of vertices and calculate total num of color
	total_vertices = len(mesh.vertex_colors[VC_NAME].data)

	#loop through each face of the selected object
	for vertex in range(0, total_vertices):

		data_path = "vertex_colors[\"%s\"].data[%s].color" %(VC_NAME, vertex)

		#settings that should be keyframed together: id and path
		keying_set.paths.add(mesh, data_path)