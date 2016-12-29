# Copyright 2016 CrowdMaster Developer Team
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of CrowdMaster.
#
# CrowdMaster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CrowdMaster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CrowdMaster.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import bpy
import mathutils
import copy

from .cm_compileBrain import compileBrain

import time
from . import cm_timings

class Agent:
    """Represents each of the agents in the scene"""
    def __init__(self, blenderid, nodeGroup, sim):
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if preferences.show_debug_options:
            print("Blender id", blenderid)
            t = time.time()
        self.id = blenderid
        self.brain = compileBrain(nodeGroup, sim, blenderid)
        self.sim = sim
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
        self.arxKey = True  # True if a keyframe was set last frame

        self.ary = objs[blenderid].rotation_euler[1]
        self.ry = 0
        self.rsy = 0
        self.aryKey = True  # True if a keyframe was set last frame

        self.arz = objs[blenderid].rotation_euler[2]
        self.rz = 0
        self.rsz = 0
        self.arzKey = True  # True if a keyframe was set last frame

        """ap - absolute pos, p - change pos by, s - speed"""
        self.apx = objs[blenderid].location[0]
        self.px = 0
        self.sx = 0
        self.apxKey = True  # True if a keyframe was set last frame

        self.apy = objs[blenderid].location[1]
        self.py = 0
        self.sy = 0
        self.apyKey = True  # True if a keyframe was set last frame

        self.apz = objs[blenderid].location[2]
        self.pz = 0
        self.sz = 0
        self.apzKey = True  # True if a keyframe was set last frame

        self.globalVelocity = mathutils.Vector([0, 0, 0])

        """Clear out the nla"""
        objs = bpy.data.objects

        objs[blenderid].animation_data_clear()
        objs[blenderid].keyframe_insert(data_path="location", frame=1)
        objs[blenderid].keyframe_insert(data_path="rotation_euler", frame=1)

        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.agent["init"] += time.time() - t

    def step(self):
        objs = bpy.data.objects
        preferences = bpy.context.user_preferences.addons[__package__].preferences

        if preferences.show_debug_options:
            t = time.time()
        self.brain.execute()
        if preferences.show_debug_options:
            if preferences.show_debug_timings:
                cm_timings.agent["brainExecute"] += time.time() - t
            if objs[self.id].select:
                print("ID: ", self.id, "Tags: ", self.brain.tags,
                      "outvars: ", self.brain.outvars)
            # TODO show this in the UI
        if preferences.show_debug_options:
            t = time.time()
        if objs[self.id] == bpy.context.active_object:
            self.brain.hightLight(bpy.context.scene.frame_current)
        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.agent["highLight"] += time.time() - t
            t = time.time()

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

        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.agent["setOutput"] += time.time() - t

    def apply(self):
        """Called in single thread after all agent.step() calls are done"""
        obj = bpy.data.objects[self.id]
        preferences = bpy.context.user_preferences.addons[__package__].preferences

        if preferences.show_debug_options:
            t = time.time()

        if obj.animation_data:
            obj.animation_data.action_extrapolation = 'HOLD_FORWARD'
            obj.animation_data.action_blend_type = 'ADD'
            for track in obj.animation_data.nla_tracks:
                track.mute = False

        """Set objects rotation and location"""

        if abs(self.arx - obj.rotation_euler[0]) > 0.000001:
            if not self.arxKey:
                obj.keyframe_insert(data_path="rotation_euler",
                                    index=0,
                                    frame=bpy.context.scene.frame_current-1)
                self.arxKey = True
            obj.rotation_euler[0] = self.arx
            obj.keyframe_insert(data_path="rotation_euler",
                                index=0,
                                frame=bpy.context.scene.frame_current)
        else:
            self.arxKey = False

        if abs(self.ary - obj.rotation_euler[1]) > 0.000001:
            if not self.aryKey:
                obj.keyframe_insert(data_path="rotation_euler",
                                    index=1,
                                    frame=bpy.context.scene.frame_current-1)
                self.aryKey = True
            obj.rotation_euler[1] = self.ary
            obj.keyframe_insert(data_path="rotation_euler",
                                index=1,
                                frame=bpy.context.scene.frame_current)
        else:
            self.aryKey = False

        if abs(self.arz - obj.rotation_euler[2]) > 0.000001:
            if not self.arzKey:
                obj.keyframe_insert(data_path="rotation_euler",
                                    index=2,
                                    frame=bpy.context.scene.frame_current-1)
                self.arzKey = True
            obj.rotation_euler[2] = self.arz
            obj.keyframe_insert(data_path="rotation_euler",
                                index=2,
                                frame=bpy.context.scene.frame_current)
        else:
            self.arzKey = False

        if abs(self.apx - obj.location[0]) > 0.000001:
            if not self.apxKey:
                obj.keyframe_insert(data_path="location",
                                    index=0,
                                    frame=bpy.context.scene.frame_current-1)
                self.apxKey = True
            obj.location[0] = self.apx
            obj.keyframe_insert(data_path="location",
                                index=0,
                                frame=bpy.context.scene.frame_current)
        else:
            self.apxKey = False

        if abs(self.apy - obj.location[1]) > 0.000001:
            if not self.apyKey:
                obj.keyframe_insert(data_path="location",
                                    index=1,
                                    frame=bpy.context.scene.frame_current-1)
                self.apyKey = True
            obj.location[1] = self.apy
            obj.keyframe_insert(data_path="location",
                                index=1,
                                frame=bpy.context.scene.frame_current)
        else:
            self.apyKey = False

        if abs(self.apz - obj.location[2]) > 0.000001:
            if not self.apzKey:
                obj.keyframe_insert(data_path="location",
                                    index=2,
                                    frame=bpy.context.scene.frame_current-1)
                self.apzKey = True
            obj.location[2] = self.apz
            obj.keyframe_insert(data_path="location",
                                index=2,
                                frame=bpy.context.scene.frame_current)
        else:
            self.apzKey = False

        self.access = copy.deepcopy(self.external)

        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.agent["applyOutput"] += time.time() - t

    def highLight(self):
        for n in self.brain.neurons.values():
            n.highLight(bpy.context.scene.frame_current)
