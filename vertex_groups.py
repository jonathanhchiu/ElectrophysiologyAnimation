bl_info = {
	"name": "Vertex Group Creater",
	"description": "Creates a vertex group with all the vertices of a mesh",
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

#Make vertex group
#bpy.ops.object.vertex_group_add()
vg = obj.vertex_groups.new('Test')

#Select vertices
#for v in mesh.vertices:
#    v.select = True

#Vertex assignment only allowed in object mode
bpy.ops.object.mode_set(mode='OBJECT')
for v in mesh.vertices:
  vg.add([v.index], 0.5, "ADD")


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
