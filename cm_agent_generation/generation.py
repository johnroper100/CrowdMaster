import bpy
import random
import mathutils
import math
import time

def generate_agents_random(locationVector):
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

            if scene.positionMode == "scene":
                newLoc = (random.uniform(scene.randomPositionMinX, scene.randomPositionMaxX), random.uniform(scene.randomPositionMinY, scene.randomPositionMaxY), ground.location.z)
            else:
                newLoc = (random.uniform(locationVector[0], scene.randomPositionMaxX), random.uniform(locationVector[1], scene.randomPositionMaxY), ground.location.z)

            newScale = random.uniform(scene.minRandSz, scene.maxRandSz)

            aName = "Armature"
            mName = "Mesh"
            for o in group_objects:
                # Reparent to new copies
                if o.parent in obs:
                    o.parent = group_objects[obs.index(o.parent)]
                else:
                    randRot = random.uniform(scene.minRandRot, scene.maxRandRot)
                    eul = mathutils.Euler((0.0, 0.0, 0.0), 'XYZ')
                    eul.rotate_axis('Z', math.radians(randRot))

                    if scene.use_rand_rot == True:
                        o.rotation_euler.rotate(eul)

                    if scene.use_rand_scale == True:
                        o.scale = (newScale, newScale, newScale)

                    o.location = newLoc

                new_group.objects.link(o)
                scene.objects.link(o)
                if o.type == 'ARMATURE':
                    aName = o.name
                if o.type == 'MESH':
                    if len(o.modifiers) == 0:
                        print("No modifiers!")
                    else:
                        for mod in o.modifiers:
                            if mod.type == "ARMATURE":
                                modName = mod.name
                                o.modifiers[modName].object = bpy.data.objects[aName]
                if scene.add_to_agent_list == True:
                    if o.type == 'ARMATURE':
                        o.select = True
                    else:
                        o.select = False

    elapsed_time = time.time() - start_time
    print("Time taken: " + str(elapsed_time))

def generate_agents_array(locationVector):
    start_time = time.time()
    scene = bpy.context.scene
    wm = bpy.context.window_manager

    number = scene.agentNumber
    rows = scene.formationArrayRows
    agentsPerRow = number/rows

    group = bpy.data.groups.get(scene.agentGroup)
    groupObjs = group.objects
    obs = [o for o in group.objects]
    ground =  bpy.data.objects[scene.groundObject]

    for obj in groupObjs:
        if scene.groundObject == obj.name:
            self.report({'ERROR'}, "The ground object must not be in the same group as the agent!")

    if group is not None:
        x = 0
        y = 0
        for row in range(rows):
            x = x + scene.formationArrayColumnMargin
            y = 0
            aName = "Armature"
            mName = "Mesh"
            for ag in range(int(agentsPerRow)):
                y = y + scene.formationArrayRowMargin
                group_objects = [o.copy() for o in obs]
                new_group = bpy.data.groups.new(scene.agentGroup)
                # Numbers will be appended automatically to the name

                newLoc = (x, y, ground.location.z)
                newScale = random.uniform(scene.minRandSz, scene.maxRandSz)

                for o in group_objects:
                    # Reparent to new copies
                    if o.parent in obs:
                        o.parent = group_objects[obs.index(o.parent)]
                    else:
                        randRot = random.uniform(scene.minRandRot, scene.maxRandRot)
                        eul = mathutils.Euler((0.0, 0.0, 0.0), 'XYZ')
                        eul.rotate_axis('Z', math.radians(randRot))

                        if scene.use_rand_rot == True:
                            o.rotation_euler.rotate(eul)

                        if scene.use_rand_scale == True:
                            o.scale = (newScale, newScale, newScale)

                        o.location = newLoc

                    new_group.objects.link(o)
                    scene.objects.link(o)
                    if o.type == 'ARMATURE':
                        aName = o.name
                    if o.type == 'MESH':
                        if len(o.modifiers) == 0:
                            print("No modifiers!")
                        else:
                            for mod in o.modifiers:
                                if mod.type == "ARMATURE":
                                    o.modifiers[modName].object = bpy.data.objects[aName]
                    if scene.add_to_agent_list == True:
                        o.select = True

    elapsed_time = time.time() - start_time
    print("Time taken: " + str(elapsed_time))
