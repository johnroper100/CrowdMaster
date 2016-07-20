import bpy
from bpy.props import *

bpy.types.Scene.startFrame = IntProperty(name="Start Frame", description="The frame on which the simulation starts.", default = 1)
bpy.types.Scene.endFrame = IntProperty(name="End Frame", description="The frame on which the simulation ends.", default = 250)
