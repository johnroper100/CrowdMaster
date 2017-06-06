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

import os
import urllib.request
from sys import platform

import bpy
from bpy.props import *
from bpy.types import Operator

from .cm_iconLoad import cicon

# Documentation Links
prefix = "http://crowdmaster.org/docs/"
documentation_mapping = (
    # OPERATORS
    # toolbar
    ("bpy.ops.scene.cm_start", "simulation/toolbar/main.html"),
    ("bpy.ops.scene.cm_stop", "simulation/toolbar/main.html"),
    ("bpy.ops.scene.cm_place_deferred_geo",
     "getting_started/utilities/place_defered_geo.html"),
    ("bpy.ops.scene.cm_setup_sample_nodes",
     "getting_started/utilities/sample_node_setups.html"),
    ("bpy.ops.scene.cm_convert_to_bound_box",
     "getting_started/utilities/conv_to_bound_box.html"),
    ("bpy.ops.scene.cm_groups_reset", "simulation/toolbar/agents.html#status"),
    ("bpy.ops.scene.cm_agent_add_selected",
     "simulation/toolbar/manual_agents.html"),
    ("bpy.ops.scene.cm_actions_populate", "simulation/toolbar/actions.html"),
    ("bpy.ops.scene.cm_actions_remove", "simulation/toolbar/actions.html"),
    ("bpy.ops.scene.cm_agents_move", "simulation/toolbar/actions.html"),
    ("bpy.ops.scene.cm_events_populate", "simulation/toolbar/events.html"),
    ("bpy.ops.scene.cm_events_remove", "simulation/toolbar/events.html"),
    ("bpy.ops.scene.cm_events_move", "simulation/toolbar/events.html"),
    ("bpy.ops.scene.cm_paths_populate", "simulation/toolbar/paths.html"),
    ("bpy.ops.scene.cm_paths_remove", "simulation/toolbar/paths.html"),
    # TODO - nodes

    # PROPS
    # toolbar
    ("bpy.types.Scene.nodeTreeType",
     "getting_started/utilities/sample_node_setups.html#node-tree-type"),
    ("bpy.types.Scene.append_to_tree",
     "getting_started/utilities/sample_node_setups.html"),
    ("bpy.types.Scene.node_tree_name",
     "getting_started/utilities/sample_node_setups.html"),
    ("bpy.types.Scene.cm_manual.groupName",
     "simulation/toolbar/manual_agents.html"),
    ("bpy.types.Scene.cm_manual.brainType",
     "simulation/toolbar/manual_agents.html"),
    # TODO - nodes
)


def doc_map():
    dm = (prefix, documentation_mapping)
    return dm


def register():
    # Register custom documentation mapping
    bpy.utils.register_manual_map(doc_map)


def unregister():
    # Unregister custom documentation mapping
    bpy.utils.unregister_manual_map(doc_map)


if __name__ == "__main__":
    register()
