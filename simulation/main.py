import bpy
import sys
#from ..nodes import main
from .. icon_load import cicon
from . import agents
from . import position

class ShowPositionGraphics(bpy.types.Operator):
    """Show the positional graphics"""
    bl_idname = "scene.cm_show_position_graphics"
    bl_label = "Show Diagram"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Showing the graphics!")

        return {'FINISHED'}

class RunSimulation(bpy.types.Operator):
    """Run CrowdMaster simulation"""
    bl_idname = "scene.cm_run_simulation"
    bl_label = "Run Simulation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        return {'FINISHED'}

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
        row.prop(scene, "agentNumber")
        
        row = layout.row()
        row.scale_y = 1.2
        if scene.agentGroup == "":
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
            row.prop(scene, "randomPositionRadius")
        
        if scene.positionType == "formation":
            row = layout.row()
            row.prop(scene, "formationPositionType")
            
            if scene.formationPositionType == "array":
                row = layout.row()
                row.prop(scene, "formationArrayX")
                
                row = layout.row()
                row.prop(scene, "formationArrayY")
