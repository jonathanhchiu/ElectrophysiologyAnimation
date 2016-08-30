bl_info = {
	"name": "Emission Node Creater",
	"description": "Creates the necessary nodes for an object's material. This is"
                    "used for illuminating the color changing heart animation",
	"author": "Tommy Truong",
	"version": (1,0),
	"category": "object",
	"blender":(2, 77, 0)
}
import bpy

def create_nodes():
    # start in object mode
    bpy.context.scene.objects.active = bpy.data.objects["Cube"]

    #grab the active object and scene
    obj = bpy.context.active_object
    mesh = obj.data

    # Get material
    mat = bpy.data.materials.get("Material")
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name="Material")

        # Assign it to object
        if mesh.materials:
            # assign to 1st material slot
            mesh.materials[0] = mat
            print("assigned mat")
        else:
            # no slots
            mesh.materials.append(mat)
            print("appended mat")

    bpy.context.object.active_material.use_nodes = True

    # get the material
    mat = bpy.data.materials['Material']

    # get the nodes
    nodes = mat.node_tree.nodes

    output = nodes.get("Material Output")
    # clear all nodes to start clean
    for node in nodes:
        if node is output:
            continue
        nodes.remove(node)

    # create ShaderNodeMixRGB node
    node_emission = nodes.new(type='ShaderNodeEmission')
    #node_mixRGB.inputs[0].default_value = (0)  # fac
    node_mixRGB.location = -300,400

    # create attr2 node
    node_attr = nodes.new(type='ShaderNodeAttribute')
    #node_attr2.inputs[3].default_value =  "Col.001" # color
    node_attr.location = -500,400

    nodes["Attribute"].attribute_name = VC_NAME

    links = mat.node_tree.links
    link_attr_emission = links.new(node_attr.outputs[0], node_emission.inputs[0])
    link_emisison_output = links.new(node_emission.outputs[0], output.inputs[0])
