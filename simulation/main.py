import bpy
import sys
from mathutils import Vector
#from ..nodes import main
from .. icon_load import cicon
from . import agents
from . import position
from . import ground

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
        groupObjs = bpy.data.groups[scene.agentGroup].objects
        halfAgents = scene.agentNumber // 2

        for object in groupObjs:
            if scene.groundObject == object.name:
                self.report({'ERROR'}, "The ground object must not be in the same group as the agent!")
        
        bpy.context.scene.objects.active.select = False
        
        if scene.positionType == "formation":
            if scene.formationPositionType == "array":
                for a in range(halfAgents):
                    obj1 = bpy.data.objects[groupObjs[1].name]
                    ground =  bpy.data.objects[scene.groundObject]
                    offset_x = (obj1.dimensions.x + scene.formationArrayX)
                    obj1.select = True
                    obj1 = obj1.copy()
                    if scene.positionMode == "vector":
                        location = Vector((scene.positionVector[0], scene.positionVector[1], ground.location.z))
                    elif scene.positionMode == "object":
                        objStart = bpy.data.objects[scene.positionObject]
                        location = Vector((objStart.location.x, objStart.location.y, ground.location.z))
                    obj1.location = location
                    scene.objects.link(obj1)
                    location.x -= offset_x

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
            row.prop(scene, "randomPositionRadius")
        
        if scene.positionType == "formation":
            row = layout.row()
            row.prop(scene, "formationPositionType")
            
            if scene.formationPositionType == "array":
                row = layout.row()
                row.prop(scene, "formationArrayX")
                
                row = layout.row()
                row.prop(scene, "formationArrayY")
