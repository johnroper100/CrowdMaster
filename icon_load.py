# Copyright 2016 CrowdMaster Developer Team
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
import bpy

ICONS = 'node_tree_logo start_sim stop_sim ' \
        'agents reset instant_setup add_agents plug code shuffle array target setup motion dice house email download'.split(' ')
icon_collection = {}


def register_icons():
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    for icon_name in ICONS:
        pcoll.load(icon_name, os.path.join(icons_dir, icon_name + '.png'), 'IMAGE')

    icon_collection["main"] = pcoll


def unregister_icons():
    for pcoll in icon_collection.values():
        bpy.utils.previews.remove(pcoll)
    icon_collection.clear()


def cicon(name):
    pcoll = icon_collection["main"]
    return pcoll[name].icon_id
