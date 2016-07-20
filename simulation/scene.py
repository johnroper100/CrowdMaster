import bpy
from bpy.props import *

bpy.types.Scene.startFrame = FloatProperty(name="Max X", description="The maximum distance in the X direction around the center point where the agents will be randomly spawned.", default = 10.0)
bpy.types.Scene.endFrame = FloatProperty(name="Max Y", description="The maximum distance in the Y direction around the center point where the agents will be randomly spawned.", default = 10.0)