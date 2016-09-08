from .cm_noiseChannels import Noise
from .cm_soundChannels import Sound
from .cm_stateChannels import State
from .cm_worldChannels import World
from .cm_crowdChannels import Crowd
from .cm_groundChannels import Ground
from .cm_formationChannels import Formation
from .cm_pathChannels import Path
from . import cm_pathChannels
Path = cm_pathChannels.Path

from .cm_masterChannels import Wrapper

def register():
    cm_pathChannels.register()

def unregister():
    cm_pathChannels.unregister()
