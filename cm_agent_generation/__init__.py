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

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        pcoll = icon_load.icon_collection["main"]
        def cicon(name):
            return pcoll[name].icon_id

        row = layout.row()
        row.prop(scene, "agentNumber")

        if scene.positionMode == "vector":
            row = layout.row()
            row.prop(scene, "positionVector")

        elif scene.positionMode == "object":
            row = layout.row()
            row.prop_search(scene, "positionObject", scene, "objects")

        row = layout.row()
        row.separator()

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(scene, "minRandRot")
        row.prop(scene, "maxRandRot")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(scene, "minRandSz")
        row.prop(scene, "maxRandSz")

        row = layout.row()
        row.separator()

        if scene.positionType == "random":
            if scene.positionMode == "scene":
                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(scene, "randomPositionMinX")
                row.prop(scene, "randomPositionMaxX")

                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(scene, "randomPositionMinY")
                row.prop(scene, "randomPositionMaxY")
            
            else:
                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(scene, "randomPositionMaxX")
                row.prop(scene, "randomPositionMaxY")

        if scene.positionType == "formation":
            if scene.formationPositionType == "array":
                row = layout.row()
                row.prop(scene, "formationArrayX")

                row = layout.row()
                row.prop(scene, "formationArrayY")
