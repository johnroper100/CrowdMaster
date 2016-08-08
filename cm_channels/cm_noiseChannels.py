import bpy
from .cm_masterChannels import MasterChannel as Mc
import random

class Noise(Mc):
    """Used to generate randomness in a scene"""
    def __init__(self, sim):
        Mc.__init__(self, sim)

    @property
    def random(self):
        """Returns a random number in range 0-1"""
        return random.random()

    @property
    def agentRandom(self):
        """Return a random number that is consistent between frames"""
        state = random.getstate()
        random.seed(hash(self.userid) - 1)
        # -1 so that this number is different to the first random number
        # generated on frame 0 (if used) of the simulation
        result = random.random()
        random.setstate(state)
        return result

    def agentMultiRandom(self, offset):
        """Return a random number that is consistent between frame but can
        be offset by an integer"""
        state = random.getstate()
        random.seed(hash(self.userid) - 1 + offset)
        # -1 so that this number is different to the first random number
        # generated on frame 0 (if used) of the simulation
        result = random.random()
        random.setstate(state)
        return result
