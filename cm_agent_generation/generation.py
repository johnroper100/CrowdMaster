import bpy
import random
import mathutils
import math
import time

def generate_agents_random(positionMode, locationVector):
    start_time = time.time()

    scene = bpy.context.scene
    wm = bpy.context.window_manager

    number = scene.agentNumber
    group = bpy.data.groups.get(scene.agentGroup)
    groupObjs = group.objects
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
                    #randRot = random.uniform(0, scene.randomPositionMaxRot)
                    #eul = mathutils.Euler((0.0, 0.0, 0.0), 'XYZ')
                    #eul.rotate_axis('Z', math.radians(randRot))
                    #scene.update()

                    if positionMode == "rectangle":
                        o.location = (random.uniform(locationVector[0], scene.randomPositionMaxX), random.uniform(locationVector[1], scene.randomPositionMaxY), ground.location.z)

                new_group.objects.link(o)
                scene.objects.link(o)

    elapsed_time = time.time() - start_time
    #print("Time taken: " + str(elapsed_time))
    return {'FINISHED'}