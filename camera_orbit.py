bl_info = {
	"name": "Camera Orbit",
	"description": "",
	"author": "Tommy Truong",
	"version": (1,0),
	"category": "object",
	"blender":(2, 77, 0)
}

import bpy

# Set to object mode
bpy.ops.object.mode_set(mode='OBJECT')

# Create an empty object
bpy.ops.object.empty_add(type='PLAIN_AXES')

# Set empty object as
obj = bpy.data.objects['Empty']

#Parent empty to object
bpy.ops.outliner.parent_drop(child="Empty", parent="Cube")

#Parent Camera to empty

#Set active object

bpy.context.scene.objects.active = obj

#Deselect active object
#obj.select = True

#Set proper keying set
ks = bpy.context.scene.keying_sets_all
ks.active = ks['Rotation']

i = 0.0
eval_time = 10

# 360 deg = 6.283 radians
while i < 6.3:

	# Jump to the next keyframe location
    bpy.context.scene.frame_set(eval_time)

	# Move camera by 0.1 rads
    obj.rotation_euler[2] = i

    #Keyframe current color
    bpy.ops.anim.keyframe_insert()

	#Rotate every 0.1 rads
    i += 0.1

    #1 keyframe per 10 frames
    eval_time += 10
