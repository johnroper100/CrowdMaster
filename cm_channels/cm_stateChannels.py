import bpy
from .cm_masterChannels import MasterChannel as Mc


class State(Mc):
    """Used for accessing the data of the current agent"""
    def __init__(self, sim):
        Mc.__init__(self, sim)
