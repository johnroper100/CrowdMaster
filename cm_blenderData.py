import bpy
from bpy.props import IntProperty, EnumProperty, CollectionProperty
from bpy.props import PointerProperty, BoolProperty, StringProperty
from bpy.types import PropertyGroup, UIList, Panel, Operator


class agent_entry(PropertyGroup):
    """The data structure for the agent entries"""
    objectName = StringProperty()
    brainType = StringProperty()
    geoGroup = StringProperty()


class group_entry(PropertyGroup):
    """For storing data about the groups created by the generation nodes"""
    groupName = StringProperty()
    agents = CollectionProperty(type=agent_entry)


def registerTypes():
    bpy.utils.register_class(agent_entry)
    bpy.utils.register_class(group_entry)
    bpy.types.Scene.cm_groups = CollectionProperty(type=group_entry)
    bpy.types.Scene.cm_groups_index = IntProperty()


def unregisterAllTypes():
    bpy.utils.unregister_class(agent_entry)
    bpy.utils.unregister_class(group_entry)
    del bpy.types.Scene.cm_groups
