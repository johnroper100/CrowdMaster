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

import math

import bpy
from mathutils import *

from .cm_masterChannels import MasterChannel as Mc
from .cm_masterChannels import timeChannel

BVHTree = bvhtree.BVHTree


class Ground(Mc):
    """Get data about the ground near the agent"""

    def __init__(self, sim):
        Mc.__init__(self, sim)
        self.channels = {}
        self.calced = False

    def newframe(self):
        for ch in self.channels.values():
            ch.newFrame()

    def setuser(self, userid):
        self.calced = False
        Mc.setuser(self, userid)

    def retrieve(self, groundGroup):
        """Return the vertical distance to the nearest ground object"""
        if groundGroup not in self.channels:
            self.channels[groundGroup] = Channel(groundGroup, self)
        self.channels[groundGroup].newuser(self.userid)
        return self.channels[groundGroup]


class Channel:
    def __init__(self, formID, Ground):
        self.Ground = Ground
        self.groupObjects = bpy.data.groups[formID].objects

        self.calcd = False
        self.groundTrees = {}
        self.store = {}
        self.aheadStore = {}

        self.userid = ""

    def newuser(self, userid):
        """Called when a new agent is using this channel"""
        self.userid = userid
        self.calcd = False
        self.aheadStore = {}

    def newFrame(self):
        """Called at the beginning of each new frame"""
        self.store = {}
        self.calcd = False
        self.groundTrees = {}

    def calcground(self):
        """Called the first time each agent uses the Ground channel"""
        results = []
        s = bpy.context.scene.objects[self.userid]
        for gnd in self.groupObjects:
            if gnd.name not in self.groundTrees:
                sce = bpy.context.scene
                self.groundTrees[gnd.name] = BVHTree.FromObject(gnd, sce)
            inverseTransform = gnd.matrix_world.inverted()
            point = (inverseTransform * s.location.to_4d()).to_3d()
            direc = Vector((0, 0, 1))
            direc.rotate(inverseTransform.to_euler())
            calcd = self.groundTrees[gnd.name].ray_cast(point,
                                                        tuple(-x for x in direc))
            if calcd[0]:
                loc, norm, ind, dist = calcd
                loc = gnd.matrix_world * loc
                norm = gnd.matrix_world * norm
                dist = (s.location - loc).length
                results.append((loc, norm, ind, dist))
            calcd = self.groundTrees[gnd.name].ray_cast(
                point, tuple(x for x in direc))
            if calcd[0]:
                loc, norm, ind, dist = calcd
                loc = gnd.matrix_world * loc
                norm = gnd.matrix_world * norm
                dist = (s.location - loc).length
                results.append((loc, norm, ind, -dist))

        if len(results) > 0:
            loc, norm, ind, dist = min(results, key=lambda x: abs(x[3]))
            self.store["location"] = loc
            self.store["normal"] = norm
            self.store["index"] = ind
            self.store["distance"] = dist
        else:
            self.store["distance"] = None
        self.calcd = True

    @timeChannel("Ground")
    def dh(self):
        if not self.calcd:
            self.calcground()
        return self.store["distance"]

    def calcAhead(self, offset):
        s = bpy.context.scene.objects[self.userid]
        result = None
        best = None
        for gnd in self.groupObjects:
            if not gnd.name in self.groundTrees:
                sce = bpy.context.scene
                self.groundTrees[gnd.name] = BVHTree.FromObject(gnd, sce)
            offsetVec = Vector((offset[0], offset[1], offset[2]))
            lookAheadPoint = s.matrix_world * offsetVec
            r = self.groundTrees[gnd.name].find_nearest(lookAheadPoint)
            if result is None or r[3] < best:
                result = r[0]
                best = r[3]
                # TODO calc distance from look ahead point to nearest point?

        if result is None:
            self.aheadStore[multiply] = {"rz": None,
                                         "rx": None}
            return
        relative = s.matrix_world.inverted() * result
        changez = math.atan2(relative[0], relative[1]) / math.pi
        changex = math.atan2(relative[2], relative[1]) / math.pi
        offsetRz = math.atan2(offset[0], offset[1]) / math.pi
        offsetRx = math.atan2(offset[2], offset[1]) / math.pi
        self.aheadStore[offset] = {"rz": changez - offsetRz,
                                   "rx": changex - offsetRx}

    @timeChannel("Ground")
    def aheadRx(self, offset):
        if offset not in self.aheadStore:
            self.calcAhead(offset)
        return self.aheadStore[offset]["rx"]

    @timeChannel("Ground")
    def aheadRz(self, offset):
        if offset not in self.aheadStore:
            self.calcAhead(offset)
        return self.aheadStore[offset]["rz"]
