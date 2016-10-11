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
import random


class Noise(Mc):
    """Used to generate randomness in a scene"""
    def __init__(self, sim):
        Mc.__init__(self, sim)

    def random(self):
        """Returns a random number in range 0-1"""
        return random.random()

    def agentRandom(self, offset=0):
        """Return a random number that is consistent between frame but can
        be offset by an integer"""
        state = random.getstate()
        random.seed(hash(self.userid) - 1 + offset)
        # -1 so that this number is different to the first random number
        # generated on frame 0 (if used) of the simulation
        result = random.random()
        random.setstate(state)
        return result
