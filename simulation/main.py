import bpy
import sys
import random
from mathutils import Vector
#from ..nodes import main
from .. icon_load import cicon
from . import scene
from . import agents
from . import position
from . import ground
from . import ui

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
        number = scene.agentNumber
        group = bpy.data.groups.get(scene.agentGroup)
        groupObjs = group.objects
        actions = [scene.agentAction1, scene.agentAction2, scene.agentAction3]
        obs = [o for o in group.objects]
        ground =  bpy.data.objects[scene.groundObject]
        
        bpy.context.scene.frame_current = 1

        for object in groupObjs:
            if scene.groundObject == object.name:
                self.report({'ERROR'}, "The ground object must not be in the same group as the agent!")
        
        bpy.context.scene.objects.active.select = False

        if group is not None:
            for g in range(number):
                group_objects = [o.copy() for o in obs]
                new_group = bpy.data.groups.new("CrowdMaster Agent")

                for o in group_objects:
                    if o.parent in obs:
                        o.parent = group_objects[obs.index(o.parent)]
                    if o.type == 'ARMATURE':
                        o.animation_data.action = bpy.data.actions[random.choice(actions)]

                        if scene.positionType == "random":
                            if scene.randomPositionMode == "rectangle":
                                if scene.positionMode == "vector":
                                    o.location = (random.uniform(scene.positionVector[0], scene.randomPositionMaxX), random.uniform(scene.positionVector[1], scene.randomPositionMaxY), ground.location.z)
                                elif scene.positionMode == "object":
                                    objStart = bpy.data.objects[scene.positionObject]
                                    o.location = (random.uniform(objStart.location.x, scene.randomPositionMaxX), random.uniform(objStart.location.y, scene.randomPositionMaxY), ground.location.z)

                    new_group.objects.link(o)
                    scene.objects.link(o)

        return {'FINISHED'}
