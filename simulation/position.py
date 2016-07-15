import bpy
from bpy.props import *

bpy.types.Scene.positionType = bpy.props.EnumProperty(
        items = [('random', 'Random', 'Agents are aligned randomly around a center point.'),
                 ('formation', 'Formation', 'Agents are aligned within a specified shape.')],
        name = "Position Type",
        description = "Which layout algorithim the simulator should use.",
        default = "random")

bpy.types.Scene.positionMode = bpy.props.EnumProperty(
        items = [('vector', 'Vector', 'The span location is specified as a list of vector coordinates.'), 
                 ('object', 'Object', 'The span location is specified as the location of an object.')],
        name = "Location Type",
        description = "Where the spawn location is pulled from.",
        default = "vector")

bpy.types.Scene.positionVector = FloatVectorProperty(name="Spawn Position", description="The location from where the agents will be spawned.", default = [0, 0, 0], subtype = "XYZ")
bpy.types.Scene.positionObject = StringProperty(name="Spawn Object", description="The object from where the agents will be spawned.")

# Random positioning
bpy.types.Scene.randomPositionRadius = FloatProperty(name="Spawn Radius", description="The radius around the center point where the agents will be randomly spawned.", default = 10.0)

# Formation positioning
bpy.types.Scene.formationPositionType = bpy.props.EnumProperty(
        items = [('array', 'Array', 'The agents are aligned in an array starting at the .'), 
                 ('shape', 'Shape', 'The span location is specified as the location of an object.')],
        name = "Formation Type",
        description = "Where the spawn location is pulled from.",
        default = "array")

bpy.types.Scene.formationArrayX = FloatProperty(name="Array X", description="The distance between each agent on the X axis.", default = 0)
bpy.types.Scene.formationArrayY = FloatProperty(name="Array Y", description="The distance between each agent on the Y axis.", default = 0)
