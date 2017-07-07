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
from bpy.types import Menu

from .cm_iconLoad import cicon


class SCENE_PT_CrowdMaster_SimTools_Pie(Menu):
    bl_label = "Simulation Tools"

    def draw(self, context):
        layout = self.layout
        preferences = context.user_preferences.addons[__package__].preferences

        pie = layout.menu_pie()
        if preferences.use_custom_icons:
            pie.operator("scene.cm_start",
                         icon_value=cicon('start_sim'))
            pie.operator("scene.cm_stop",
                         icon_value=cicon('stop_sim'))
        else:
            pie.operator("scene.cm_start", icon='FILE_TICK')
            pie.operator("scene.cm_stop", icon='CANCEL')
        pie.operator("scene.cm_place_deferred_geo", icon="EDITMODE_HLT")


def register():
    bpy.utils.register_class(SCENE_PT_CrowdMaster_SimTools_Pie)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Window")
    kmi = km.keymap_items.new("wm.call_menu_pie", "M", "PRESS", shift=True,
                              alt=True).properties.name = "SCENE_PT_CrowdMaster_SimTools_Pie"


def unregister():
    bpy.utils.unregister_class(SCENE_PT_CrowdMaster_SimTools_Pie)
