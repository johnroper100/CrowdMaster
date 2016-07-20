import bpy
import sys
from .. icon_load import cicon

class CrowdMasterUIMain(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "CrowdMaster"
    bl_label = "Main"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.prop_search(scene, "agentGroup", bpy.data, "groups")
        
        row = layout.row()
        row.prop_search(scene, "groundObject", scene, "objects")
        
        row = layout.row()
        row.prop(scene, "agentNumber")
        
        row = layout.row()
        row.scale_y = 1.2
        if (scene.agentGroup == "") or (scene.groundObject == ""):
            row.enabled = False
        row.operator("scene.cm_run_simulation", icon_value=cicon('run_sim'))

class CrowdMasterUIPosition(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "CrowdMaster"
    bl_label = "Position"
    
    @classmethod
    def poll(self, context):
        try:
            scene = context.scene
            return (scene.agentGroup)
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
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

class CrowdMasterUIAnim(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "CrowdMaster"
    bl_label = "Animation"
    
    @classmethod
    def poll(self, context):
        try:
            scene = context.scene
            return (scene.agentGroup)
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.prop_search(scene, "agentAction1", bpy.data, "actions")
        
        row = layout.row()
        row.prop_search(scene, "agentAction2", bpy.data, "actions")

        row = layout.row()
        row.prop_search(scene, "agentAction3", bpy.data, "actions")