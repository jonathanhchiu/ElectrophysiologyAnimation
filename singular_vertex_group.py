bl_info = {
	"name": "Vertex Group Creater",
	"description": "Creates a vertex group for each vertiex in a mesh",
	"author": "Tommy Truong",
	"version": (1,0),
	"category": "object",
	"blender":(2, 77, 0)
}
import bpy

#Set active object
obj = bpy.context.scene.objects['Cube']
mesh = obj.data
bpy.context.scene.objects.active = obj

#Deselect active object
obj.select = True

#Set edit mode
#bpy.ops.object.mode_set(mode='EDIT')

#Deselect
#bpy.ops.mesh.select_all(action='TOGGLE')

#Make vertex group for each vertex
#bpy.ops.object.vertex_group_add()
#vg = obj.vertex_groups.new('Test')
#empty_vgroups = [None] * len(mesh.vertices)
for i in range(0, len(mesh.vertices)):
	obj.vertex_groups.new(str(i))

#Select vertices
#for v in mesh.vertices:
#    v.select = True

#Vertex assignment only allowed in object mode
bpy.ops.object.mode_set(mode='OBJECT')
i = 0
j = 0.0
for vg in obj.vertex_groups:
	vg.add([i], j, 'ADD')
	i += 1
	j += 0.1

#for v in mesh.vertices:
#  vg.add([v.index], 0.5, "ADD")


#create vertex group dict w/names
vgroup_names = {vgroup.index: vgroup.name for vgroup in obj.vertex_groups}

# create dictionary of vertex group assignments per vertex
vgroups = {v.index: [vgroup_names[g.group] for g in v.groups] for v in mesh.vertices}



#Make vertex group
#bpy.ops.object.vertex_group_assign()

#Get vertex group
#obj.vertex_groups

#for v in obj.data.vertices:
#  print(v)
#  print("before")
#  for g in v.groups:
#      print("In here")
