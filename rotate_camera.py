bl_info = {
	"name": "Rotate Camera",
	"description": "Camera rotation animation",
	"author": "Tommy Truong",
	"version": (1,0),
	"category": "object",
	"blender":(2, 77, 0)
}

import bpy

#Set to object mode
bpy.ops.object.mode_set(mode='OBJECT')

#Get empty object
obj = bpy.data.objects['Empty']

#Parent empty to object
#Parent Camera to empty

#Set active object
mesh = obj.data
bpy.context.scene.objects.active = obj

#Deselect active object
#obj.select = True

#Set proper keying set
ks = bpy.context.scene.keying_sets_all
ks.active = ks['Rotation']

i = 0.0
eval_time = 10

while i < 6.5:

    	#Move cursor to next keyframe location
    bpy.context.scene.frame_set(eval_time)

    	#Rotate
    obj.rotation_euler[2] = i

    #Keyframe current color
    bpy.ops.anim.keyframe_insert()

    	#Rotate every 0.1 rads
    i += 0.1

    #1 keyframe per 10 frames
    eval_time += 10
