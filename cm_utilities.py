import bpy
import os
from bpy.props import IntProperty, EnumProperty, CollectionProperty
from bpy.props import PointerProperty, BoolProperty, StringProperty
from bpy.types import PropertyGroup, UIList, Panel, Operator
from . import icon_load
from . icon_load import cicon

bpy.types.Scene.show_utilities = BoolProperty(
		name="Show or hide the utilities",
		description="Show/hide the utilities",
		default=False,
		options={'HIDDEN'}
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
        
        box = layout.box()

        row = box.row()
        row.label("General:", icon='FILE_TICK')

def register():
    bpy.utils.register_class(CrowdMaster_setup_sample_nodes)

def unregister():
    bpy.utils.unregister_class(CrowdMaster_setup_sample_nodes)

if __name__ == "__main__":
    register()
