import bpy
import os
from bpy.types import Panel, Operator
from bpy.props import FloatProperty, StringProperty, BoolProperty
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty

from . import icon_load
from . icon_load import cicon

bpy.types.Scene.show_utilities = BoolProperty(
		name="Show or hide the utilities",
		description="Show/hide the utilities",
		default=False,
		options={'HIDDEN'}
	)

bpy.types.Scene.nodeTreeType = EnumProperty(
        items = [("sim", "Simulation", "Simulation node setups"),
                 ("gen", "Generation", "Generation node setups")],
        name = "Node Tree Type",
        description = "Which node tree setups to show",
        default = "gen"
    )

class CrowdMaster_setup_sample_nodes(bpy.types.Operator):
    bl_idname = "scene.cm_setup_sample_nodes"
    bl_label = "Sample Node Setups"

    def execute(self, context):
        scene = context.scene 

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600)
    
    def check(self, context):
        scene = context.scene

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        if scene.nodeTreeType == "gen":
            row = layout.row()
            row.operator("scene.cm_gennodes_pos_random_simple", icon_value=cicon('shuffle'))

        elif scene.nodeTreeType == "sim":
            row = layout.row()
            row.label("Sample simulation node setups: TODO")

class CrowdMaster_genNodes_pos_random_simple(bpy.types.Operator):
    bl_idname = "scene.cm_gennodes_pos_random_simple"
    bl_label = "Simple Random Positioning"

    def execute(self, context):
        scene = context.scene
        
        ng = bpy.data.node_groups.new("SimpleRandomPositioning", "CrowdMasterAGenTreeType")

        object_node = ng.nodes.new("ObjectInputNodeType")
        object_node.location = (-600, 0)
        
        template_node = ng.nodes.new("TemplateNodeType")
        template_node.location = (-400, 0)
        template_node.brainType = "Sample Random"
        
        rand_node = ng.nodes.new("RandomPositionNodeType")
        rand_node.location = (-200, 0)
        rand_node.noToPlace = 25
        rand_node.radius = 25.00
        
        gen_node = ng.nodes.new("GenerateNodeType")
        gen_node.location = (0, 0)
        
        links = ng.links
        link = links.new(object_node.outputs[0], template_node.inputs[0])
        link = links.new(template_node.outputs[0], rand_node.inputs[0])
        link = links.new(rand_node.outputs[0], gen_node.inputs[0])

        return {'FINISHED'}

class CrowdMaster_convert_to_bound_box(bpy.types.Operator):
    bl_idname = "scene.cm_convert_to_bound_box"
    bl_label = "Convert Selected To Bounding Box"

    def execute(self, context):
        scene = context.scene
        
        selected = bpy.context.selected_objects
        for obj in selected:
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            bpy.ops.mesh.primitive_cube_add() 
            bound_box = bpy.context.active_object 

            bound_box.location = obj.location
            bound_box.rotation_euler = obj.rotation_euler
            bound_box.select = True

        return {'FINISHED'}

def register():
    bpy.utils.register_class(CrowdMaster_setup_sample_nodes)
    bpy.utils.register_class(CrowdMaster_convert_to_bound_box)
    bpy.utils.register_class(CrowdMaster_genNodes_pos_random_simple)

def unregister():
    bpy.utils.unregister_class(CrowdMaster_setup_sample_nodes)
    bpy.utils.unregister_class(CrowdMaster_convert_to_bound_box)
    bpy.utils.unregister_class(CrowdMaster_genNodes_pos_random_simple)

if __name__ == "__main__":
    register()
