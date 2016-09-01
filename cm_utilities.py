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

bpy.types.Scene.bbox_joinObjects = BoolProperty(name="Join Objects", description="Join all the created bounding box meshes into one object", default=False)
bpy.types.Scene.bbox_margin = FloatProperty(name="Margin", description="Scale each bounding box by this")

class CrowdMaster_setup_sample_nodes(bpy.types.Operator):
    bl_idname = "scene.cm_setup_sample_nodes"
    bl_label = "Sample Node Setups"
    
    nodeTreeType = EnumProperty(
        items = [("sim", "Simulation", "Simulation node setups"),
                 ("gen", "Generation", "Generation node setups")],
        name = "Node Tree Type",
        description = "Which node tree setups to show",
        default = "gen"
    )

    def execute(self, context):
        scene = context.scene 

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600)
    
    def check(self, context):
        scene = context.scene
        if self.nodeTreeType != self.nodeTreeType:
            return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.prop(self, "nodeTreeType")

class CrowdMaster_convert_to_bound_box(bpy.types.Operator):
    bl_idname = "scene.cm_convert_to_bound_box"
    bl_label = "Convert Selected To Bounding Box"

    def execute(self, context):
        scene = context.scene 

        return {'FINISHED'}

def register():
    bpy.utils.register_class(CrowdMaster_setup_sample_nodes)
    bpy.utils.register_class(CrowdMaster_convert_to_bound_box)

def unregister():
    bpy.utils.unregister_class(CrowdMaster_setup_sample_nodes)
    bpy.utils.unregister_class(CrowdMaster_convert_to_bound_box)

if __name__ == "__main__":
    register()
