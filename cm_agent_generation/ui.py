import bpy
import sys
from .. import icon_load

class CrowdMasterUIPosition(bpy.types.Panel):
    bl_label = "Agent Generation"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "CrowdMaster"
    
    @classmethod
    def poll(self, context):
        try:
             return bpy.context.space_data.tree_type == 'CrowdMasterTreeType'
        except (AttributeError, KeyError, TypeError):
            return False
            return False

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        pcoll = icon_load.icon_collection["main"]
        def cicon(name):
            return pcoll[name].icon_id
        
        if scene.use_agent_generation == True:
            row = layout.row()
            row.prop(scene, "positionMode")

            if scene.positionMode == "vector":
                row = layout.row()
                row.prop(scene, "positionVector")

            elif scene.positionMode == "object":
                row = layout.row()
                row.prop_search(scene, "positionObject", scene, "objects")

            row = layout.row()
            row.separator()

            row = layout.row()
            row.prop(scene, "positionType")

            if scene.positionType == "random":   
                row = layout.row()
                row.prop(scene, "randomPositionMode")

                row = layout.row()
                row.prop(scene, "randomPositionMaxRot")

                if scene.randomPositionMode == "rectangle":
                    row = layout.row()
                    row.prop(scene, "randomPositionMaxX")

                    row = layout.row()
                    row.prop(scene, "randomPositionMaxY")

                if scene.randomPositionMode == "circle":
                    row = layout.row()
                    row.prop(scene, "randomPositionRadius")

            if scene.positionType == "formation":
                row = layout.row()
                row.prop(scene, "formationPositionType")

                if scene.formationPositionType == "array":
                    row = layout.row()
                    row.prop(scene, "formationArrayX")

                    row = layout.row()
                    row.prop(scene, "formationArrayY")
        else:
            row = layout.row()
            row.label("Enable agent generation to use this feature!", icon='MOD_ARRAY')

def gen_register():
    bpy.utils.register_class(CrowdMasterUIPosition)

def gen_unregister():
    bpy.utils.unregister_class(CrowdMasterUIPosition)
