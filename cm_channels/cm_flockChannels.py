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
import mathutils
from mathutils import Vector

from .cm_masterChannels import MasterChannel as Mc
from .cm_masterChannels import timeChannel


class Flock(Mc):
    """Used for flocking behaviour"""

    def __init__(self, sim):
        Mc.__init__(self, sim)

        self.separateCache = {}
        self.alignCache = {}
        self.cohereCache = {}

    def newframe(self):
        self.separateCache = {}
        self.alignCache = {}
        self.cohereCache = {}

    # ==== FLOCKING ====

    def _hashSet(self, s):
        """An experiment for how to cache the results of calculations when the
        input is a set"""
        s = 1
        for item in s:
            s *= hash(item) % (10**25) + 1
        return s

    def calcSeparate(self, localArea):
        sepVec = Vector([0, 0, 0])
        if len(localArea) == 0:
            return sepVec
        agents = self.sim.agents
        for neighbour in localArea:
            sepVec.x += agents[self.userid].apx - agents[neighbour].apx
            sepVec.y += agents[self.userid].apy - agents[neighbour].apy
            sepVec.z += agents[self.userid].apz - agents[neighbour].apz

        z = mathutils.Matrix.Rotation(agents[self.userid].arz, 4, 'Z')
        y = mathutils.Matrix.Rotation(agents[self.userid].ary, 4, 'Y')
        x = mathutils.Matrix.Rotation(agents[self.userid].arx, 4, 'X')

        rotation = x * y * z
        relative = sepVec * rotation
        return relative

    def calcAlign(self, localArea):
        alnVec = Vector([0, 0, 0])
        if len(localArea) == 0:
            return alnVec
        agents = self.sim.agents
        for neighbour in localArea:
            alnVec.x += agents[neighbour].arx
            alnVec.y += agents[neighbour].ary
            alnVec.z += agents[neighbour].arz
        alnVec /= len(localArea)

        alnVec.x -= agents[self.userid].arx
        alnVec.y -= agents[self.userid].ary
        alnVec.z -= agents[self.userid].arz

        alnVec.x %= 2 * math.pi
        alnVec.y %= 2 * math.pi
        alnVec.z %= 2 * math.pi

        if alnVec.x < math.pi:
            alnVec.x = alnVec.x / math.pi
        else:
            alnVec.x = -2 + alnVec.x / math.pi
        if alnVec.y < math.pi:
            alnVec.y = alnVec.y / math.pi
        else:
            alnVec.y = -2 + alnVec.y / math.pi
        if alnVec.z < math.pi:
            alnVec.z = alnVec.z / math.pi
        else:
            alnVec.z = -2 + alnVec.z / math.pi
        return alnVec

    def calcCohere(self, localArea):
        cohVec = Vector([0, 0, 0])
        if len(localArea) == 0:
            return cohVec
        agents = self.sim.agents
        for neighbour in localArea:
            cohVec.x += agents[neighbour].apx
            cohVec.y += agents[neighbour].apy
            cohVec.z += agents[neighbour].apz
        cohVec /= len(localArea)
        cohVec.x -= agents[self.userid].apx
        cohVec.y -= agents[self.userid].apy
        cohVec.z -= agents[self.userid].apz

        z = mathutils.Matrix.Rotation(agents[self.userid].arz, 4, 'Z')
        y = mathutils.Matrix.Rotation(agents[self.userid].ary, 4, 'Y')
        x = mathutils.Matrix.Rotation(agents[self.userid].arx, 4, 'X')

        rotation = x * y * z
        relative = cohVec * rotation
        return relative

    @timeChannel()
    def separateTx(self, inputs):
        """The amount to move on the x axis (ie. left-right) away from the
        average position of close neighbours"""
        inSet = set()
        for into in inputs:
            for i in into:
                inSet.add(i)
        if len(inSet) == 0:
            return None
        sepVec = self.calcSeparate(inSet)
        return sepVec[0]

    @timeChannel()
    def separateTy(self, inputs):
        """The amount to move on the y axis (ie. forward-backward) away from the
        average position of close neighbours (ie. slow down - speed up)"""
        inSet = set()
        for into in inputs:
            for i in into:
                inSet.add(i)
        if len(inSet) == 0:
            return None
        sepVec = self.calcSeparate(inSet)
        return sepVec[1]

    @timeChannel()
    def separateTz(self, inputs):
        """The amount to move on the z axis (ie. up-down) away from the
        average position of close neighbours"""
        inSet = set()
        for into in inputs:
            for i in into:
                inSet.add(i)
        if len(inSet) == 0:
            return None
        sepVec = self.calcSeparate(inSet)
        return sepVec[2]

    @timeChannel()
    def alignRz(self, inputs):
        """The amount to rotate about the z axis (ie. turn left-right) to
        align with the direction of neighbours"""
        inSet = set()
        for into in inputs:
            for i in into:
                inSet.add(i)
        if len(inSet) == 0:
            return None
        alnVec = self.calcAlign(inSet)
        return alnVec.z

    @timeChannel()
    def alignRx(self, inputs):
        """The amount to rotate about the x axis (ie. turn up-down) to
        align with the direction of neighbours"""
        inSet = set()
        for into in inputs:
            for i in into:
                inSet.add(i)
        if len(inSet) == 0:
            return None
        alnVec = self.calcAlign(inSet)
        return alnVec.x

    @timeChannel()
    def cohereTx(self, inputs):
        """The amount to move on the x axis (ie. left-right) towards the average
        position of neighbours"""
        inSet = set()
        for into in inputs:
            for i in into:
                inSet.add(i)
        if len(inSet) == 0:
            return None
        cohVec = self.calcCohere(inSet)
        return cohVec[0]

    @timeChannel()
    def cohereTy(self, inputs):
        """The amount to move on the y axis (ie. forward-backward) towards the
        average position of neighbours"""
        inSet = set()
        for into in inputs:
            for i in into:
                inSet.add(i)
        if len(inSet) == 0:
            return None
        cohVec = self.calcCohere(inSet)
        return cohVec[1]

    @timeChannel()
    def cohereTz(self, inputs):
        """The amount to move on the z axis (ie. up-down) towards the average
        position of neighbours"""
        inSet = set()
        for into in inputs:
            for i in into:
                inSet.add(i)
        if len(inSet) == 0:
            return None
        cohVec = self.calcCohere(inSet)
        return cohVec[2]
