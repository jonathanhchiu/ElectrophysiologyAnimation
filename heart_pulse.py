bl_info = {
	"name": "Shape Key Key framer",
	"description": "Places 4 heart pulse key frames",
	"author": "Tommy Truong",
	"version": (1,0),
	"category": "object",
	"blender":(2, 77, 0)
}
import bpy

#frames per keyframe
eval_time = 10

#clear dopesheet
bpy.context.area.type = 'DOPESHEET_EDITOR'
bpy.ops.action.delete()
bpy.context.area.type = 'TEXT_EDITOR'

#grab the heart object
obj = bpy.context.scene.objects.active

#grab pickled object
mesh = obj.data

#grab the shape key
key = mesh.shape_keys

#3 pulses
pulse = 0
i = 0
j = 0
increment = 2

#add all 8 key frames
while i < 8:

#    if pulse == 2:
#        #print("here")
#        #Move cursor to next keyframe location
#        bpy.context.scene.frame_set((j*5) + increment)
#        increment *= 2.5
#        print(bpy.context.scene.frame_current)

#        #Change evaluation time eval_time (eval_time should increment by 10 for each frame in sequence)
#        key.eval_time = eval_time

#        #Make a keyframe with the shape key at this eval_time
#        key.keyframe_insert(data_path="eval_time")
    if pulse == 4:
        break
    else:
        #Move cursor to next keyframe location
        bpy.context.scene.frame_set(j*5)

        #Change evaluation time eval_time (eval_time should increment by 10 for each frame in sequence)
        key.eval_time = eval_time

        #Make a keyframe with the shape key at this eval_time
        key.keyframe_insert(data_path="eval_time")

    #print(i, pulse, eval_time)
    #If loop finishes, restart
    if pulse == 0:
        if i == 7:
            pulse += 1
            i = 0
            eval_time = 70
        else:
            i += 1
            eval_time += 10
    elif pulse < 4:
        if (pulse % 2) == 1:
            if i == 6:
                pulse += 1
                i = 0
                eval_time = 20
            else:
                i += 1
                eval_time -= 10

        elif (pulse % 2) == 0:
            if i == 6:
                pulse += 1
                i = 0
                eval_time = 70
            else:
                i += 1
                eval_time += 10

    j += 1
