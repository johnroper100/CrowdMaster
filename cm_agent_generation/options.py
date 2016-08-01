import bpy
from bpy.props import *

bpy.types.Scene.use_agent_generation = BoolProperty(
        name = "Use Agent Generation",
        description = "Generate agents to be simulated.",
        default = True,
        )

bpy.types.Scene.agentGroup = StringProperty(name="Base Agent", description="The group that holds the mesh and armature for the base agent that is duplicated.")
bpy.types.Scene.agentNumber = IntProperty(name="Number of Agents", description="Number of agents to be generated.", default=100)
bpy.types.Scene.groundObject = StringProperty(name="Ground Object", description="The object that will be used as a ground in the simulation.")

bpy.types.Scene.positionType = bpy.props.EnumProperty(
        items = [('random', 'Random', 'Agents are aligned randomly around a center point.'),
                 ('formation', 'Formation', 'Agents are aligned within a specified shape.')],
        name = "Position Type",
        description = "Which layout algorithim the simulator should use.",
        default = "random")

bpy.types.Scene.maxRandRot = FloatProperty(name="Max Rotation", description="The maximum random rotation in the Z axis for each agent.", default = 360.0, max=360.0)
bpy.types.Scene.minRandRot = FloatProperty(name="Min Rotation", description="The minimum random rotation in the Z axis for each agent.", default = 0.0, min=-360.0)

bpy.types.Scene.maxRandSz = FloatProperty(name="Max Scale", description="The maximum random scale for each agent.", default = 5.0)
bpy.types.Scene.minRandSz = FloatProperty(name="Min Scale", description="The minimum random scale for each agent.", default = 0.0)

bpy.types.Scene.positionMode = bpy.props.EnumProperty(
        items = [('vector', 'Vector', 'The span location is specified as a list of vector coordinates.'), 
                 ('object', 'Object', 'The span location is specified as the location of an object.')],
        name = "Location Type",
        description = "Where the spawn location is pulled from.",
        default = "vector")

bpy.types.Scene.positionVector = FloatVectorProperty(name="Spawn Position", description="The location from where the agents will be spawned.", default = [0, 0, 0], subtype = "XYZ")
bpy.types.Scene.positionObject = StringProperty(name="Spawn Object", description="The object from where the agents will be spawned.")

# Random positioning
bpy.types.Scene.randomPositionMode = bpy.props.EnumProperty(
        items = [('rectangle', 'Rectangle', 'The agents are spawned inside a specified rectangle.'), 
                 ('circle', 'Circle', 'The agents are spawned inside a circle.')],
        name = "Random Position Type",
        description = "Where shape inside which the agents are spawned.",
        default = "rectangle")

bpy.types.Scene.randomPositionRadius = FloatProperty(name="Spawn Radius", description="The radius around the center point where the agents will be randomly spawned.", default = 10.0)

bpy.types.Scene.randomPositionMaxX = FloatProperty(name="Max X", description="The maximum distance in the X direction around the center point where the agents will be randomly spawned.", default = 50.0)
bpy.types.Scene.randomPositionMaxY = FloatProperty(name="Max Y", description="The maximum distance in the Y direction around the center point where the agents will be randomly spawned.", default = 50.0)

# Formation positioning
bpy.types.Scene.formationPositionType = bpy.props.EnumProperty(
        items = [('array', 'Array', 'The agents are aligned in an array starting at the point specified.'), 
                 ('shape', 'Shape', 'The span location is specified as the location of an object.')],
        name = "Formation Type",
        description = "Where the spawn location is pulled from.",
        default = "array")

bpy.types.Scene.formationArrayX = FloatProperty(name="Array X", description="The distance between each agent on the X axis.", default = 0)
bpy.types.Scene.formationArrayY = FloatProperty(name="Array Y", description="The distance between each agent on the Y axis.", default = 0)
