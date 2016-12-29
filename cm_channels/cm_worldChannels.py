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
from .cm_masterChannels import MasterChannel as Mc
from .cm_masterChannels import timeChannel

import math
import mathutils


class World(Mc):
    """Used to access other data from the scene"""
    def __init__(self, sim):
        Mc.__init__(self, sim)
        self.store = {}

    def target(self, target):
        """Dynamic properties"""
        if target not in self.store:
            self.store[target] = Channel(target, self.userid, self.sim)
        return self.store[target]

    def newframe(self):
        self.store = {}

    def setuser(self, userid):
        self.store = {}
        Mc.setuser(self, userid)

    @property
    def time(self):
        return bpy.context.scene.frame_current


class Channel:
    def __init__(self, target, user, sim):
        self.sim = sim

        self.target = target
        self.userid = user

        self.store = {}
        self.calcd = False

    def calculate(self):
        O = bpy.context.scene.objects

        to = O[self.target]
        ag = O[self.userid]
        userDim = self.sim.agents[self.userid].dimensions

        tDim = max(self.sim.agents[self.target].dimensions)
        uDim = max(userDim)

        difx = to.location.x - ag.location.x
        dify = to.location.y - ag.location.y
        difz = to.location.z - ag.location.z
        dist = math.sqrt(difx**2 + dify**2 + difz**2)

        target = to.location - ag.location

        z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
        y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
        x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')

        rotation = x * y * z
        relative = target * rotation

        changez = math.atan2(relative[0], relative[1])/math.pi
        changex = math.atan2(relative[2], relative[1])/math.pi
        self.store = {"rz": changez,
                      "rx": changex,
                      "arrived": 1 if dist < (tDim + uDim) else 0}

        self.calcd = True

    @property
    @timeChannel("World")
    def rz(self):
        if not self.calcd:
            self.calculate()
        return self.store["rz"]

    @property
    @timeChannel("World")
    def rx(self):
        if not self.calcd:
            self.calculate()
        return self.store["rx"]

    @property
    @timeChannel("World")
    def arrived(self):
        if not self.calcd:
            self.calculate()
        return self.store["arrived"]
