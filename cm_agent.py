# Copyright 2017 CrowdMaster Developer Team
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

import copy
import logging
import time

import bpy
import mathutils

from . import cm_timings
from .cm_compileBrain import compileBrain

logger = logging.getLogger("CrowdMaster")


class Agent:
    """Represents each of the agents in the scene."""

    def __init__(self, blenderid, nodeGroup, sim, rigOverwrite, constrainBone,
                 tags=None, modifyBones=None, freezeAnimation=False, geoGroup=None):
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if preferences.show_debug_options:
            t = time.time()
        self.id = blenderid
        self.brain = compileBrain(nodeGroup, sim, blenderid, freezeAnimation)
        self.sim = sim
        self.external = {"id": self.id, "tags": {
            t.name: t.value for t in tags}}
        """self.external modified by the agent and then coppied to self.access
        at the end of the frame so that the updated values can be accessed by
        other agents"""
        self.access = copy.deepcopy(self.external)

        self.freezeAnimation = freezeAnimation

        self.geoGroup = geoGroup

        self.rigOverwrite = rigOverwrite
        self.constrainBone = constrainBone
        self.modifyBones = {}
        if modifyBones is not None:
            for m in modifyBones:
                if m.name not in self.modifyBones:
                    self.modifyBones[m.name] = {}
                self.modifyBones[m.name][m.attribute] = m.tag

        objs = bpy.data.objects

        """Set the dimensions of this object"""
        self.dimensions = objs[blenderid].dimensions
        self.radius = max(self.dimensions) / 2

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

        self.shapeKeys = {}
        self.lastShapeKeys = set()

        """Clear out the nla"""
        if not freezeAnimation:
            objs[blenderid].animation_data_clear()
            objs[blenderid].keyframe_insert(data_path="location", frame=1)
            objs[blenderid].keyframe_insert(
                data_path="rotation_euler", frame=1)

        # Keyframe everything so agent return to the same position.
        if self.geoGroup is None or self.geoGroup == "":
            # ie. manual agent
            if self.rigOverwrite != "":
                obj = objs[self.id]
                if obj.type == "ARMATURE":
                    for bone in obj.pose.bones:
                        bone.keyframe_insert("location")
                        if bone.rotation_mode == "QUATERNION":
                            bone.keyframe_insert("rotation_quaternion")
                        elif bone.rotation_mode == "AXIS_ANGLE":
                            bone.keyframe_insert("rotation_axis_angle")
                        else:
                            bone.keyframe_insert("rotation_euler")
                obj.keyframe_insert("location")
                if obj.rotation_mode == "QUATERNION":
                    obj.keyframe_insert("rotation_quaternion")
                elif obj.rotation_mode == "AXIS_ANGLE":
                    obj.keyframe_insert("rotation_axis_angle")
                else:
                    obj.keyframe_insert("rotation_euler")
        else:
            # ie. auto generated agent
            for obj in bpy.data.groups[self.geoGroup].objects:
                if obj.type == "ARMATURE":
                    for bone in obj.pose.bones:
                        bone.keyframe_insert("location")
                        if bone.rotation_mode == "QUATERNION":
                            bone.keyframe_insert("rotation_quaternion")
                        elif bone.rotation_mode == "AXIS_ANGLE":
                            bone.keyframe_insert("rotation_axis_angle")
                        else:
                            bone.keyframe_insert("rotation_euler")
                obj.keyframe_insert("location")
                if obj.rotation_mode == "QUATERNION":
                    obj.keyframe_insert("rotation_quaternion")
                elif obj.rotation_mode == "AXIS_ANGLE":
                    obj.keyframe_insert("rotation_axis_angle")
                else:
                    obj.keyframe_insert("rotation_euler")

        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.agent["init"] += time.time() - t

    def step(self):
        """Called each frame of the simulation."""

        objs = bpy.data.objects
        preferences = bpy.context.user_preferences.addons[__package__].preferences

        rot = objs[self.id].rotation_euler

        if preferences.show_debug_options:
            t = time.time()
        self.brain.execute()
        if preferences.show_debug_options:
            if preferences.show_debug_timings:
                cm_timings.agent["brainExecute"] += time.time() - t
            if objs[self.id].select:
                logger.debug("ID: {} Tags: {} outvars: {}".format(
                    self.id, self.brain.tags, self.brain.outvars))
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

        self.shapeKeys = self.brain.outvars["sk"]

        self.external["tags"] = self.brain.tags

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

        self.access = copy.deepcopy(self.external)

        if self.freezeAnimation:
            return

        if preferences.show_debug_options:
            t = time.time()

        if obj.animation_data:
            obj.animation_data.action_extrapolation = 'HOLD_FORWARD'
            obj.animation_data.action_blend_type = 'ADD'
            for track in obj.animation_data.nla_tracks:
                track.mute = False

        """Set objects shape key value, rotation and location"""

        lastFrame = bpy.context.scene.frame_current - 1
        thisFrame = bpy.context.scene.frame_current

        if self.geoGroup is None or self.geoGroup == "":
            grpObjs = [obj]
        else:
            grpObjs = bpy.data.groups[self.geoGroup].objects

        for cobj in grpObjs:
            if cobj.type == 'MESH':
                if cobj.data.shape_keys is not None:
                    for skNm in self.shapeKeys:
                        sk = cobj.data.shape_keys.key_blocks.get(skNm)
                        if sk is not None:
                            skVal = self.shapeKeys[skNm]
                            if abs(sk.value - skVal) > 0.000001:
                                if skNm not in self.lastShapeKeys:
                                    sk.keyframe_insert(
                                        data_path="value", frame=lastFrame)
                                    self.lastShapeKeys.add(skNm)
                                sk.value = skVal
                                sk.keyframe_insert(
                                    data_path="value", frame=thisFrame)
                            else:
                                if skNm in self.lastShapeKeys:
                                    self.lastShapeKeys.remove(skNm)

        if abs(self.arx - obj.rotation_euler[0]) > 0.000001:
            if not self.arxKey:
                obj.keyframe_insert(data_path="rotation_euler",
                                    index=0,
                                    frame=lastFrame)
                self.arxKey = True
            obj.rotation_euler[0] = self.arx
            obj.keyframe_insert(data_path="rotation_euler",
                                index=0,
                                frame=thisFrame)
        else:
            self.arxKey = False

        if abs(self.ary - obj.rotation_euler[1]) > 0.000001:
            if not self.aryKey:
                obj.keyframe_insert(data_path="rotation_euler",
                                    index=1,
                                    frame=lastFrame)
                self.aryKey = True
            obj.rotation_euler[1] = self.ary
            obj.keyframe_insert(data_path="rotation_euler",
                                index=1,
                                frame=thisFrame)
        else:
            self.aryKey = False

        if abs(self.arz - obj.rotation_euler[2]) > 0.000001:
            if not self.arzKey:
                obj.keyframe_insert(data_path="rotation_euler",
                                    index=2,
                                    frame=lastFrame)
                self.arzKey = True
            obj.rotation_euler[2] = self.arz
            obj.keyframe_insert(data_path="rotation_euler",
                                index=2,
                                frame=thisFrame)
        else:
            self.arzKey = False

        if abs(self.apx - obj.location[0]) > 0.000001:
            if not self.apxKey:
                obj.keyframe_insert(data_path="location",
                                    index=0,
                                    frame=lastFrame)
                self.apxKey = True
            obj.location[0] = self.apx
            obj.keyframe_insert(data_path="location",
                                index=0,
                                frame=thisFrame)
        else:
            self.apxKey = False

        if abs(self.apy - obj.location[1]) > 0.000001:
            if not self.apyKey:
                obj.keyframe_insert(data_path="location",
                                    index=1,
                                    frame=lastFrame)
                self.apyKey = True
            obj.location[1] = self.apy
            obj.keyframe_insert(data_path="location",
                                index=1,
                                frame=thisFrame)
        else:
            self.apyKey = False

        if abs(self.apz - obj.location[2]) > 0.000001:
            if not self.apzKey:
                obj.keyframe_insert(data_path="location",
                                    index=2,
                                    frame=lastFrame)
                self.apzKey = True
            obj.location[2] = self.apz
            obj.keyframe_insert(data_path="location",
                                index=2,
                                frame=thisFrame)
        else:
            self.apzKey = False

        objs = bpy.context.scene.objects

        modArm = None
        if objs[self.id].type == 'Armature':
            modArm = objs[self.id]
        if self.rigOverwrite is not None and self.rigOverwrite != "":
            modArm = objs[self.rigOverwrite]

        if modArm is not None:
            for bone in self.modifyBones:
                for attribute in self.modifyBones[bone]:
                    tag = self.modifyBones[bone][attribute]
                    tags = self.external["tags"]
                    if tag in tags:
                        tagVal = tags[tag]
                        if bone in modArm.pose.bones:
                            boneObj = modArm.pose.bones[bone]
                            if attribute == "RX":
                                boneObj.rotation_euler[0] = tagVal
                                boneObj.keyframe_insert(data_path="rotation_euler",
                                                        index=0,
                                                        frame=thisFrame)
                            if attribute == "RY":
                                boneObj.rotation_euler[1] = tagVal
                                boneObj.keyframe_insert(data_path="rotation_euler",
                                                        index=1,
                                                        frame=thisFrame)
                            if attribute == "RZ":
                                boneObj.rotation_euler[2] = tagVal
                                boneObj.keyframe_insert(data_path="rotation_euler",
                                                        index=2,
                                                        frame=thisFrame)

        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.agent["applyOutput"] += time.time() - t

    def highLight(self):
        for n in self.brain.neurons.values():
            n.highLight(bpy.context.scene.frame_current)
