import bpy
from bpy.props import *

bpy.types.Scene.positionType = bpy.props.EnumProperty(
        items = [('formation', 'Formation', 'Agents are aligned within a specified shape'), 
                 ('random', 'Random', 'Agents are aligned randomly around a center point')],
        name = "Position Type",
        default = "random")
