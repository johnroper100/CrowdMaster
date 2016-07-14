import bpy
from bpy.props import *

bpy.types.Scene.positionType = bpy.props.EnumProperty(
        items = [('formation', 'Formation', 'Agents are aligned within a specified shape.'), 
                 ('random', 'Random', 'Agents are aligned randomly around a center point.')],
        name = "Position Type",
        description = "Which layout algorithim the simulator should use.",
        default = "random")

bpy.types.Scene.randomPositionType = bpy.props.EnumProperty(
        items = [('vector', 'Vector', 'The span location is specified as a list of vector coordinates.'), 
                 ('object', 'Object', 'The span location is specified as the location of an object.')],
        name = "Location Type",
        description = "Where the spawn location is pulled from.",
        default = "vector")

bpy.types.Scene.randomPositionVector = FloatVectorProperty(name="Spawn Position", description="The location around which the agents will be randomly spawned.", default = [0, 0, 0], subtype = "XYZ")
bpy.types.Scene.randomPositionObject = StringProperty(name="Spawn Object", description="The object from where the agents will be spawned.")
bpy.types.Scene.randomPositionRadius = FloatProperty(name="Spawn Radius", description="The radius around the center point where the agents will be randomly spawned.", default = 10.0)
