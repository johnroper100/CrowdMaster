# Copyright 2017 CrowdMaster Developer Team
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of CrowdMaster.
#
# CrowdMaster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CrowdMaster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CrowdMaster.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import (BoolProperty, CollectionProperty, EnumProperty,
                       FloatProperty, IntProperty, PointerProperty,
                       StringProperty)
from bpy.types import Operator, Panel, PropertyGroup, UIList


def updateStartFrame(self, context):
    start = context.scene.cm_sim_start_frame
    end = context.scene.cm_sim_end_frame
    if start >= end:
        start = end


def updateEndFrame(self, context):
    start = context.scene.cm_sim_start_frame
    end = context.scene.cm_sim_end_frame
    if end <= start:
        end = start


bpy.types.Scene.cm_sim_start_frame = IntProperty(
    name="Simulation Start Frame",
    default=1,
    update=updateStartFrame,
)
bpy.types.Scene.cm_sim_end_frame = IntProperty(
    name="Simulation End Frame",
    default=250,
    update=updateEndFrame,
)


class modifyBoneProperty(PropertyGroup):
    """For storing bone - tag pairs"""
    # name - Name of the bone
    tag = StringProperty()  # Name of tag to attach value to
    attribute = StringProperty()


class initialTagProperty(PropertyGroup):
    """For storing a dictionary like structure of initial tags."""
    # name - Name of the tag
    value = FloatProperty()


class agent_entry(PropertyGroup):
    """The data structure for the agent entries."""
    # name - The name of the blender object
    geoGroup = StringProperty()
    initialTags = CollectionProperty(type=initialTagProperty)
    rigOverwrite = StringProperty()
    constrainBone = StringProperty()
    modifyBones = CollectionProperty(type=modifyBoneProperty)


class agent_type_entry(PropertyGroup):
    """Contains a list of agents of a certain type.
    Useful to separate into agents of each type to make collecting statistics
    easier/more efficient."""
    # name - The type of brain contained in this list
    agents = CollectionProperty(type=agent_entry)


class group_entry(PropertyGroup):
    """For storing data about the groups created by the generation nodes."""
    # name - The label given to this group
    agentTypes = CollectionProperty(type=agent_type_entry)
    totalAgents = IntProperty(default=0)
    groupType = EnumProperty(items=[("auto", "Auto", "Created by nodes"),
                                    ("manual", "Manual", "Manually added")], default="auto")
    freezePlacement = BoolProperty(name="Freeze Placement", default=False)
    freezeAnimation = BoolProperty(name="Freeze Animation", default=False)


class manual_props(PropertyGroup):
    """All settings for manually adding agents."""
    groupName = StringProperty()
    brainType = StringProperty()


def registerTypes():
    bpy.utils.register_class(modifyBoneProperty)
    bpy.utils.register_class(initialTagProperty)
    bpy.utils.register_class(agent_entry)
    bpy.utils.register_class(agent_type_entry)
    bpy.utils.register_class(group_entry)

    bpy.types.Scene.cm_groups = CollectionProperty(type=group_entry)
    bpy.types.Scene.cm_groups_index = IntProperty()

    bpy.types.Scene.cm_view_details = BoolProperty(name="View Group Details",
                                                   description="Show a breakdown of the agents in the selected group",
                                                   default=False)
    bpy.types.Scene.cm_view_details_index = IntProperty()

    bpy.utils.register_class(manual_props)
    bpy.types.Scene.cm_manual = PointerProperty(type=manual_props)
    bpy.types.Scene.cm_switch_dupli_group_suffix = StringProperty(
        name="Dupli Group Suffix")
    bpy.types.Scene.cm_switch_dupli_group_target = StringProperty(
        name="Dupli Group Target")


def unregisterAllTypes():
    bpy.utils.unregister_class(modifyBoneProperty)
    bpy.utils.unregister_class(initialTagProperty)
    bpy.utils.unregister_class(agent_entry)
    bpy.utils.unregister_class(agent_type_entry)
    bpy.utils.unregister_class(group_entry)

    bpy.utils.unregister_class(manual_props)

    del bpy.types.Scene.cm_groups
    del bpy.types.Scene.cm_groups_index
    del bpy.types.Scene.cm_view_details
    del bpy.types.Scene.cm_view_details_index
    del bpy.types.Scene.cm_manual
    del bpy.types.Scene.cm_switch_dupli_group_suffix
    del bpy.types.Scene.cm_switch_dupli_group_target
