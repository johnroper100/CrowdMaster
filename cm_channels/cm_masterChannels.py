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
        self.randstate = hash(userid) + self.sim.framelast
        random.seed(self.randstate)


class Wrapper:
    """This is so that the channel can decide how to handle retrievals"""
    def __init__(self, channel, *args):
        self.channel = channel

    def __getattr__(self, attr):
        """When attribute retrieved for object wrapped by this pass it on to
        the contained channel in the correct form"""
        if attr in self.channel.__dir__():
            return getattr(self.channel, attr)
        else:
            return self.channel.retrieve(attr)
