import bpy
import os
from bpy.props import IntProperty, EnumProperty, CollectionProperty
from bpy.props import PointerProperty, BoolProperty, StringProperty
from bpy.types import PropertyGroup, UIList, Panel, Operator

bpy.types.Scene.show_utilities = BoolProperty(
		name="Show or hide the utilities",
		description="Show/hide the utilities",
		default=False,
		options={'HIDDEN'}
	)

class SCENE_PT_CrowdMasterUtilities(Panel):
    """Creates CrowdMaster utilities panel in the node editor."""
    bl_label = "Utilities"
    bl_idname = "SCENE_PT_CrowdMasterUtilities"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "CrowdMaster"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        try:
             return bpy.context.space_data.tree_type == 'CrowdMasterTreeType', context.space_data.tree_type == 'CrowdMasterGenTreeType'
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout

def register():
    bpy.utils.register_class(SCENE_PT_CrowdMasterUtilities)

def unregister():
    bpy.utils.unregister_class(SCENE_PT_CrowdMasterUtilities)

if __name__ == "__main__":
    register()
