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

# Documentation Links
prefix = "http://crowdmaster.org/docs/"
documentation_mapping = (
    # OPERATORS
    # toolbar
    ("bpy.ops.scene.cm_start", "simulation/toolbars/main/index.html#start-simulation"),
    ("bpy.ops.scene.cm_stop", "simulation/toolbars/main/index.html#stop-simulation"),
    ("bpy.ops.scene.cm_place_deferred_geo",
     "simulation/toolbars/main/utilities/place_deferred_geo.html"),
    ("bpy.ops.scene.cm_switch_dupli_groups",
     "simulation/toolbars/main/utilities/switch_dupli_groups.html"),
    ("bpy.ops.scene.cm_groups_reset", "simulation/toolbars/agents.html#reset-group"),
    ("bpy.ops.scene.cm_agent_add_selected",
     "simulation/toolbars/manual_agents.html"),
    ("bpy.ops.scene.cm_actions_populate", "simulation/toolbars/actions.html"),
    ("bpy.ops.scene.cm_actions_remove", "simulation/toolbars/actions.html"),
    ("bpy.ops.scene.cm_agents_move", "simulation/toolbars/actions.html"),
    ("bpy.ops.scene.cm_events_populate", "simulation/toolbars/events.html"),
    ("bpy.ops.scene.cm_events_remove", "simulation/toolbars/events.html"),
    ("bpy.ops.scene.cm_events_move", "simulation/toolbars/events.html"),
    ("bpy.ops.scene.cm_paths_populate", "simulation/toolbars/paths.html"),
    ("bpy.ops.scene.cm_paths_remove", "simulation/toolbars/paths.html"),
    ("bpy.ops.view3d.cm_paths_bfs",
     "simulation/toolbars/paths.html#breadth-first-search-to-direct-edges"),
    ("bpy.ops.view3d.cm_paths_dfs",
     "simulation/toolbars/paths.html#depth-first-search-to-direct-edges"),
    ("bpy.ops.view3d.cm_switch_connected_path",
     "simulation/toolbars/paths.html#switch-the-direction-of-the-connected-edges"),
    ("bpy.ops.view3d.cm_switch_selected_path",
     "simulation/toolbars/paths.html#switch-the-direction-of-the-selected-edges"),
    ("bpy.ops.view3d.draw_path_operator",
     "simulation/toolbars/paths.html#draw-directions"),
    # TODO - nodes

    # PROPS
    # toolbar
    ("bpy.types.Scene.cm_sim_start_frame",
     "simulation/toolbars/main/index.html#simulation-start-frame"),
    ("bpy.types.Scene.cm_sim_end_frame",
     "simulation/toolbars/main/index.html#simulation-end-frame"),
    ("bpy.types.Scene.cm_manual.groupName",
     "simulation/toolbars/manual_agents.html"),
    ("bpy.types.Scene.cm_manual.brainType",
     "simulation/toolbars/manual_agents.html"),
    ("bpy.types.Scene.cm_switch_dupli_group_suffix",
     "simulation/toolbars/main/utilities/switch_dupli_groups.html#dupli-group-suffix"),
    ("bpy.types.Scene.cm_switch_dupli_group_target",
     "simulation/toolbars/main/utilities/switch_dupli_groups.html#dupli-group-target"),
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
