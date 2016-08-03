import bpy
import sys
from .. import icon_load
from . import options
from .ui import gen_register, gen_unregister
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
        row.prop_search(scene, "agentGroup", bpy.data, "groups")

        row = layout.row()
        row.prop_search(scene, "groundObject", scene, "objects")

        row = layout.row()
        row.prop(scene, "agentNumber")
        
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
        row.prop(scene, "minRandRot")

        row = layout.row()
        row.prop(scene, "maxRandRot")

        row = layout.row()
        row.scale_y = 0.25
        row.separator()

        row = layout.row()
        row.prop(scene, "minRandSz")

        row = layout.row()
        row.prop(scene, "maxRandSz")

        row = layout.row()
        row.separator()

        row = layout.row()
        row.prop(scene, "positionType")

        if scene.positionType == "random":   
            row = layout.row()
            row.prop(scene, "randomPositionMaxX")

            row = layout.row()
            row.prop(scene, "randomPositionMaxY")

        if scene.positionType == "formation":
            row = layout.row()
            row.prop(scene, "formationPositionType")

            if scene.formationPositionType == "array":
                row = layout.row()
                row.prop(scene, "formationArrayX")

                row = layout.row()
                row.prop(scene, "formationArrayY")
