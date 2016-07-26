import bpy
from bpy.props import *
import mathutils
import math

bpy.types.Scene.agentGroup = StringProperty(name="Base Agent", description="The group that holds the mesh and armature for the base agent that is duplicated.")
bpy.types.Scene.agentNumber = IntProperty(name="Number of Agents", description="Number of agents to be generated.", default=100)

bpy.types.Scene.agentAction1 = StringProperty(name="Action 1", description="The first action.")
bpy.types.Scene.agentAction2 = StringProperty(name="Action 2", description="The second action.")
bpy.types.Scene.agentAction3 = StringProperty(name="Action 3", description="The second action.")

def getAgentBounds(agent):
    """Set the dimensions of this object"""
    agentDimensions = bpy.data.objects[agent].dimensions
    agentRadius = max(agentDimensions) / 2
