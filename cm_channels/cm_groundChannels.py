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

from mathutils import *
BVHTree = bvhtree.BVHTree

from .cm_masterChannels import MasterChannel as Mc


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

        self.userid = ""

    def newuser(self, userid):
        """Called when a new agent is using this channel"""
        self.userid = userid
        self.calcd = False

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
                r = gnd.rotation_euler
                if r[0] or r[1] or r[2]:
                    print(gnd.name, "rotation must be applied")
                    # TODO make ray_cast work with rotation
                sce = bpy.context.scene
                self.groundTrees[gnd.name] = BVHTree.FromObject(gnd, sce)
            point = s.location - gnd.location
            calcd = self.groundTrees[gnd.name].ray_cast(point, (0, 0, -1))
            if calcd[0]:
                results.append(calcd + (1,))
            calcd = self.groundTrees[gnd.name].ray_cast(point, (0, 0, 1))
            if calcd[0]:
                results.append(calcd + (-1,))

        if len(results) > 0:
            loc, norm, ind, dist, direc = min(results, key=lambda x: x[3])
            self.store["location"] = loc
            self.store["normal"] = norm
            self.store["index"] = ind
            self.store["distance"] = dist * direc  # direc is +/-1
        else:
            self.store["distance"] = 0
        self.calcd = True

    def dh(self):
        if not self.calcd:
            self.calcground()
        return self.store["distance"]
