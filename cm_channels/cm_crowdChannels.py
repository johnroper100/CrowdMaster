import bpy
from .cm_masterChannels import MasterChannel as Mc


class Crowd(Mc):
    """Used to access the data of other agents"""
    def __init__(self, sim):
        Mc.__init__(self, sim)

    def allagents(self):
        return bpy.context.scene.cm_agents
