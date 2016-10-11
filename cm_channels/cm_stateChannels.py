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


class State(Mc):
    """Used for accessing the data of the current agent"""
    def __init__(self, sim):
        Mc.__init__(self, sim)

    @property
    def radius(self):
        return bpy.context.scene.objects[self.userid].dimensions.length/2

    @property
    def userObject(self):
        """Shoudn't really ever be used but here for when a feature is missing"""
        return bpy.context.scene.objects[self.userid]

    @property
    def vars(self):
        """Get last frames agent variables. (Has to be last frames because this
        frames variables can be changed during the evaluation of the brain)"""
        return self.sim.agents[self.userid].access

    @property
    def speed(self):
        """Get the distance travelled in the last frame"""
        return self.sim.agents[self.userid].globalVelocity.length

    @property
    def velocity(self):
        """The vector of the change in position for the last frame"""
        return self.sim.agents[self.userid].globalVelocity
