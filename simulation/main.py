import bpy
import sys
import random
from mathutils import Vector
#from ..nodes import main
from .. icon_load import cicon
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
        groupObjs = bpy.data.groups[scene.agentGroup].objects
        actions = [scene.agentAction1, scene.agentAction2, scene.agentAction3]

        for object in groupObjs:
            if scene.groundObject == object.name:
                self.report({'ERROR'}, "The ground object must not be in the same group as the agent!")
        
        bpy.context.scene.objects.active.select = False
        
        if scene.positionType == "formation":
            if scene.formationPositionType == "array":
                halfAgents = scene.agentNumber // 2
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

        if scene.positionType == "random":
            if scene.randomPositionMode == "rectangle":
                number = scene.agentNumber
                group = bpy.data.groups.get(scene.agentGroup)
                if group is not None:
                    for g in range(number):
                        group_objects = [o.copy() for o in bpy.data.groups[scene.agentGroup].objects]
                        new_group = bpy.data.groups.new("CrowdMaster Agent")
                        for o in group_objects:
                            if o.type == 'ARMATURE':
                                o.animation_data.action = random.choice(actions)
                            new_group.objects.link(o)
                            scene.objects.link(o)

        return {'FINISHED'}
