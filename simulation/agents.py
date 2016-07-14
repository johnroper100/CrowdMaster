import bpy
from bpy.props import *

bpy.types.Scene.agentGroup = StringProperty(name="Base Agent", description="The group that holds the mesh and armature for the base agent that is duplicated")
bpy.types.Scene.agentNumber = IntProperty(name="Number of Agents", description="Number of agents to be generated", default=100)
