import bpy
import sys
from .. import icon_load
from . import options
from .generation import generate_agents_random, generate_agents_array

class CrowdMaster_generate_agents(bpy.types.Operator):
    bl_idname = "scene.cm_gen_agents"
    bl_label = "Generate Agents"

    def execute(self, context):
        scene = context.scene
        if scene.use_agent_generation == True:
            if scene.positionMode == "vector":
                vector = [scene.positionVector[0], scene.positionVector[1]]
            elif scene.positionMode == "object":
                objStart = bpy.data.objects[scene.positionObject]
                vector = [objStart.location.x, objStart.location.y]

            if scene.positionType == "random":
                generate_agents_random(vector)

            if scene.positionType == "formation":
                if scene.formationPositionType == "array":
                    generate_agents_array(vector)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600)
    
    def check(self, context):
        if self.use_rand_rot is True:
            return True
        if self.use_rand_scale is True:
            return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        box = layout.box()
        
        pcoll = icon_load.icon_collection["main"]
        def cicon(name):
            return pcoll[name].icon_id

        row = box.row()
        row.prop(scene, "agentNumber")
        
        if scene.positionType == "formation":
            if scene.formationPositionType == "array":
                row = box.row()
                row.prop(scene, "formationArrayRows")

        if scene.positionMode == "vector":
            row = box.row()
            row.prop(scene, "positionVector")

        elif scene.positionMode == "object":
            row = box.row()
            row.prop_search(scene, "positionObject", scene, "objects")
        
        box = layout.box()

        row = box.row()
        row.prop(scene, "use_rand_rot")

        row = box.row(align=True)
        row.alignment = 'EXPAND'
        if scene.use_rand_rot == False:
            row.enabled = False
        row.prop(scene, "minRandRot")
        row.prop(scene, "maxRandRot")
        
        row = box.row()
        row.prop(scene, "use_rand_scale")

        row = box.row(align=True)
        row.alignment = 'EXPAND'
        if scene.use_rand_scale == False:
            row.enabled = False
        row.prop(scene, "minRandSz")
        row.prop(scene, "maxRandSz")

        if scene.positionType == "random":
            box = layout.box()
    
            if scene.positionMode == "scene":
                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(scene, "randomPositionMinX")
                row.prop(scene, "randomPositionMaxX")

                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(scene, "randomPositionMinY")
                row.prop(scene, "randomPositionMaxY")
            
            else:
                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(scene, "randomPositionMaxX")
                row.prop(scene, "randomPositionMaxY")
