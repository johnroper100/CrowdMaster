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

from .cm_masterChannels import MasterChannel as Mc
from .cm_masterChannels import timeChannel


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
