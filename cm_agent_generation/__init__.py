import bpy
from . import options
from .ui import gen_register, gen_unregister
from .generation import generate_agents_random

class CrowdMaster_generate_agents(bpy.types.Operator):
    bl_idname = "scene.cm_gen_agents"
    bl_label = "Generate Agents"

    def execute(self, context):
        scene = context.scene
        if scene.use_agent_generation == True:
            if scene.positionType == "random":
                if scene.positionMode == "vector":
                    vector = [scene.positionVector[0], scene.positionVector[1]]
                elif scene.positionMode == "object":
                    objStart = bpy.data.objects[scene.positionObject]
                    vector = [objStart.location.x, objStart.location.y]
                generate_agents_random(scene.randomPositionMode, vector)
        return {'FINISHED'}
