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

from ..libs import cm_accelerate
from .cm_masterChannels import MasterChannel as Mc
from .cm_masterChannels import timeChannel

Vector = mathutils.Vector


class AgentInfo(Mc):
    """Used to get information about other agent in a scene"""

    @timeChannel("AgentInfo")
    def getTag(self, inputs, tag):
        """For each agent in the input look up their tag"""
        result = {}
        for into in inputs:
            for i in into:
                if i in self.sim.agents:
                    agentTags = self.sim.agents[i].access["tags"]
                    if tag in agentTags:
                        result[i] = agentTags[tag]
        return result

    @timeChannel("AgentInfo")
    def headingRz(self, inputs):
        """For each agent in the input look up the relative heading about the
        z axis"""
        result = {}
        ag = bpy.context.scene.objects[self.userid]
        rotMat = self.sim.agents[self.userid].rotationMatrix
        for into in inputs:
            for i in into:
                emitterAgent = self.sim.agents[i]
                # eVel = emitterAgent.globalVelocity

                z = mathutils.Matrix.Rotation(-emitterAgent.arz, 4, 'Z')
                y = mathutils.Matrix.Rotation(-emitterAgent.ary, 4, 'Y')
                x = mathutils.Matrix.Rotation(-emitterAgent.arx, 4, 'X')

                rotation = x * y * z
                emitHead = Vector((0, 1, 0)) * rotation

                headRz, headRx = cm_accelerate.relativeRotation(emitHead.x,
                                                                emitHead.y,
                                                                emitHead.z,
                                                                ag.location.x,
                                                                ag.location.y,
                                                                ag.location.z,
                                                                rotMat)
                result[i] = headRz
        return result

    @timeChannel("AgentInfo")
    def headingRx(self, inputs):
        """For each agent in the input look up the relative heading about the
        x axis"""
        result = {}
        ag = bpy.context.scene.objects[self.userid]
        for into in inputs:
            for i in into:
                emitterAgent = self.sim.agents[i]
                # eVel = emitterAgent.globalVelocity

                z = mathutils.Matrix.Rotation(-emitterAgent.arz, 4, 'Z')
                y = mathutils.Matrix.Rotation(-emitterAgent.ary, 4, 'Y')
                x = mathutils.Matrix.Rotation(-emitterAgent.arx, 4, 'X')

                rotation = x * y * z
                emitHead = Vector((0, 1, 0)) * rotation

                headRz, headRx = cm_accelerate.relativeRotation(emitHead.x,
                                                                emitHead.y,
                                                                emitHead.z,
                                                                ag.location.x,
                                                                ag.location.y,
                                                                ag.location.z,
                                                                rotMat)
                result[i] = headRx
        return result
