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

class MasterChannel:
    """The parent class for all the channels"""
    def __init__(self, sim):
        self.sim = sim
        self.userid = ""

    def newframe(self):
        """Override this in child classes if they store data"""
        pass

    @property
    def retrieve(self):
        """Override this in child classes for dynamic properties"""
        return 0

    def register(self, agent, frequency, val):
        """Override this in child classes to define channels"""
        pass

    def setuser(self, userid):
        """Set up the channel to be used with a new agent"""
        self.userid = userid
