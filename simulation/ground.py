import bpy
from bpy.props import *

bpy.types.Scene.groundObject = StringProperty(name="Ground Object", description="The object that will be used as a ground in the simulation.")
