import bpy
import time
import mathutils
import copy
import math

from .cm_compileBrain import compileBrain
from .cm_debuggingMode import debugMode


class Agent:
    """Represents each of the agents in the scene"""
    def __init__(self, blenderid, nodeGroup, sim):
        if debugMode:
            print("Blender id", blenderid)
        self.id = blenderid
        self.brain = compileBrain(nodeGroup, sim, blenderid)
        self.sim = sim
        # print(self, self.brain.type)
        self.external = {"id": self.id, "tags": {}}
        """self.external modified by the agent and then coppied to self.access
        at the end of the frame so that the updated values can be accessed by
        other agents"""
        self.access = copy.deepcopy(self.external)
        self.agvars = {"None": None}
        "agent variables. Don't access from other agents"

        objs = bpy.data.objects

        """Set the dimensions of this object"""
        self.dimensions = objs[blenderid].dimensions
        self.radius = max(self.dimensions) / 2
        # TODO allow the user to specify a bounding geometry

        """ar - absolute rot, r - change rot by, rs - rot speed"""
        self.arx = objs[blenderid].rotation_euler[0]
        self.rx = 0
        self.rsx = 0

        self.ary = objs[blenderid].rotation_euler[1]
        self.ry = 0
        self.rsy = 0

        self.arz = objs[blenderid].rotation_euler[2]
        self.rz = 0
        self.rsz = 0

        """ap - absolute pos, p - change pos by, s - speed"""
        self.apx = objs[blenderid].location[0]
        self.px = 0
        self.sx = 0

        self.apy = objs[blenderid].location[1]
        self.py = 0
        self.sy = 0

        self.apz = objs[blenderid].location[2]
        self.pz = 0
        self.sz = 0
        
        self.globalVelocity = mathutils.Vector([0,0,0])

        """Clear out the nla"""
        objs = bpy.data.objects

        objs[blenderid].animation_data_clear()
        objs[blenderid].keyframe_insert(data_path="location", frame=1)
        objs[blenderid].keyframe_insert(data_path="rotation_euler", frame=1)

    def step(self):
        objs = bpy.data.objects

        self.brain.execute()
        if objs[self.id].select:
            if debugMode:
                print("ID: ", self.id, "Tags: ", self.brain.tags,
                      "outvars: ", self.brain.outvars)
            # TODO show this in the UI
        if objs[self.id] == bpy.context.active_object:
            self.brain.hightLight(bpy.context.scene.frame_current)

        self.rx = self.brain.outvars["rx"] if self.brain.outvars["rx"] else 0
        self.ry = self.brain.outvars["ry"] if self.brain.outvars["ry"] else 0
        self.rz = self.brain.outvars["rz"] if self.brain.outvars["rz"] else 0

        self.arx += self.rx + self.rsx
        self.rx = 0

        self.ary += self.ry + self.rsy
        self.ry = 0

        self.arz += self.rz + self.rsz
        self.rz = 0

        self.px = self.brain.outvars["px"] if self.brain.outvars["px"] else 0
        self.py = self.brain.outvars["py"] if self.brain.outvars["py"] else 0
        self.pz = self.brain.outvars["pz"] if self.brain.outvars["pz"] else 0

        self.external["tags"] = self.brain.tags
        self.agvars = self.brain.agvars

        move = mathutils.Vector((self.px + self.sx,
                                 self.py + self.sy,
                                 self.pz + self.sz))

        z = mathutils.Matrix.Rotation(-self.arz, 4, 'Z')
        y = mathutils.Matrix.Rotation(-self.ary, 4, 'Y')
        x = mathutils.Matrix.Rotation(-self.arx, 4, 'X')

        rotation = x * y * z
        result = move * rotation

        self.globalVelocity = result

        self.apx += result[0]

        self.apy += result[1]

        self.apz += result[2]

    def apply(self):
        """Called in single thread after all agent.step() calls are done"""
        objs = bpy.data.objects

        if objs[self.id].animation_data:
            objs[self.id].animation_data.action_extrapolation = 'HOLD_FORWARD'
            objs[self.id].animation_data.action_blend_type = 'ADD'

        """Set objects rotation and location"""
        objs[self.id].rotation_euler = (self.arx, self.ary, self.arz)
        objs[self.id].location = (self.apx, self.apy, self.apz)
        if objs[self.id].animation_data:
            for track in objs[self.id].animation_data.nla_tracks:
                track.mute = False

        """Set the keyframes"""
        objs[self.id].keyframe_insert(data_path="rotation_euler",
                                      frame=bpy.context.scene.frame_current)
        objs[self.id].keyframe_insert(data_path="location",
                                      frame=bpy.context.scene.frame_current)

        self.access = copy.deepcopy(self.external)

    def highLight(self):
        for n in self.brain.neurons.values():
            n.highLight(bpy.context.scene.frame_current)
