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

    for obj in groupObjs:
        if scene.groundObject == obj.name:
            self.report({'ERROR'}, "The ground object must not be in the same group as the agent!")

    if group is not None:
        for g in range(number):
            group_objects = [o.copy() for o in obs]
            new_group = bpy.data.groups.new(scene.agentGroup)
            # Numbers will be appended automatically to the name

            newLoc = (random.uniform(locationVector[0], scene.randomPositionMaxX), random.uniform(locationVector[1], scene.randomPositionMaxY), ground.location.z)
            newScale = random.uniform(scene.minRandSz, scene.maxRandSz)

            for o in group_objects:
                if o.parent in obs:
                    o.parent = group_objects[obs.index(o.parent)]
                    # Reparent to new copies?

                if o.type == 'ARMATURE' or o.type == 'MESH':
                    randRot = random.uniform(scene.minRandRot, scene.maxRandRot)
                    eul = mathutils.Euler((0.0, 0.0, 0.0), 'XYZ')
                    eul.rotate_axis('Z', math.radians(randRot))

                    o.rotation_euler.rotate(eul)
                    
                    o.scale = (newScale, newScale, newScale)

                    if positionMode == "rectangle":
                        o.location = newLoc

                new_group.objects.link(o)
                scene.objects.link(o)

    elapsed_time = time.time() - start_time
    print("Time taken: " + str(elapsed_time))
