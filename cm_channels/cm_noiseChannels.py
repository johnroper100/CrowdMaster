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

import random

import numpy as np

import bpy

from .cm_masterChannels import MasterChannel as Mc
from .cm_masterChannels import timeChannel


class Noise(Mc):
    """Used to generate randomness in a scene"""

    def __init__(self, sim):
        Mc.__init__(self, sim)

    @timeChannel("Noise")
    def random(self):
        """Returns a random number in range 0-1"""
        return random.random()

    @timeChannel("Noise")
    def agentRandom(self, offset=0):
        """Return a random number that is consistent between frames but can
        be offset by an integer"""
        state = random.getstate()
        random.seed(hash(self.userid) - 1 + offset)
        # -1 so that this number is different to the first random number
        # generated on frame 0 (if used) of the simulation
        result = random.random()
        random.setstate(state)
        return result

    @timeChannel("Noise")
    def sinWave(self, swtm=1.0, swa=5):
        """Returns a sine wave section in range -1 - 1 based on the current frame"""
        return np.cos((bpy.context.scene.frame_current * swtm) * 3.14 / swa)
