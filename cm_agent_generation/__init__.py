import bpy
from . import options
from .ui import gen_register, gen_unregister
from .generation import generate_agents_array

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
