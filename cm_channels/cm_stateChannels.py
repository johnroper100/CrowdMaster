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
