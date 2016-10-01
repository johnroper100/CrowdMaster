import random


class MasterChannel:
    """The parent class for all the channels"""
    def __init__(self, sim):
        self.sim = sim

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
