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

import logging
import os

import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty
from bpy.types import AddonPreferences, Operator

from . import addon_updater_ops
from .cm_iconLoad import cicon

logger = logging.getLogger("CrowdMaster")


class CMSavePrefs(Operator):
    """Save the CrowdMaster preferences """
    bl_idname = "scene.cm_save_prefs"
    bl_label = "Save Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.wm.save_userpref()

        return {'FINISHED'}


def updateLogger(self, context):
    preferences = context.user_preferences.addons[__package__].preferences
    if preferences.show_debug_options:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')


class CMPreferences(AddonPreferences):
    bl_idname = __package__
    scriptdir = bpy.path.abspath(os.path.dirname(__file__))

    auto_check_update = BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=True,
    )

    updater_intrval_months = IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days = IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=5,
        min=0,
    )
    updater_intrval_hours = IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes = IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    use_custom_icons = BoolProperty(
        name="Use Custom Icons",
        description="Chose whether to use the custom icons that come with the addon or not.",
        default=True,
    )

    show_debug_options = BoolProperty(
        name="Show Debug Options",
        description="Chose whether to show the debug options in the interface. This also enables debug mode.",
        default=False,
        update=updateLogger,
    )

    show_debug_timings = BoolProperty(
        name="Show Debug Timings",
        description="Time and print to console the times taken by elements of the system.",
        default=False,
    )

    play_animation = BoolProperty(
        name="Start Animation Automatically",
        description="Start and stop the animation automatically when the start and stop sim buttons are pressed.",
        default=True,
    )

    ask_to_save = BoolProperty(
        name="Ask To Save",
        description="Chose whether the current file has to be saved or not before simulating or generating.",
        default=True,
    )

    use_node_color = BoolProperty(
        name="Use Node Color",
        description="Choose whether or not to show the node info colors while simulating.",
        default=True,
    )

    prefs_tab_items = [
        ("GEN", "General Settings", "General settings for the addon."),
        ("UPDATE", "Addon Update Settings", "Settings for the addon updater."),
        ("DEBUG", "Debug Options", "Debug settings and utilities.")]

    prefs_tab = EnumProperty(name="Options Set", items=prefs_tab_items)

    def draw(self, context):
        layout = self.layout
        preferences = context.user_preferences.addons[__package__].preferences

        row = layout.row()
        row.prop(preferences, "prefs_tab", expand=True)

        if preferences.prefs_tab == "GEN":
            row = layout.row()
            row.prop(preferences, 'use_custom_icons', icon_value=cicon('plug'))

            if preferences.use_custom_icons:
                row.prop(preferences, 'play_animation',
                         icon_value=cicon('shuffle'))
            else:
                row.prop(preferences, 'play_animation', icon='ACTION')

            row = layout.row()
            row.prop(preferences, 'ask_to_save', icon='SAVE_AS')
            row.prop(preferences, 'use_node_color', icon='COLOR')

            row = layout.row()
            if preferences.use_custom_icons:
                row.prop(preferences, 'show_debug_options',
                         icon_value=cicon('code'))
            else:
                row.prop(preferences, 'show_debug_options',
                         icon='RECOVER_AUTO')

        if preferences.prefs_tab == "UPDATE":
            layout.row()
            addon_updater_ops.update_settings_ui(self, context)

        if preferences.prefs_tab == "DEBUG":
            if preferences.show_debug_options:
                row = layout.row()
                row.scale_y = 1.25
                row.operator("scene.cm_run_short_tests", icon='CONSOLE')

                #row = layout.row()
                #row.scale_y = 1.25
                #row.operator("scene.cm_run_long_tests", icon='QUIT')

                row = layout.row()
                row.scale_y = 1.25
                row.prop(preferences, 'show_debug_timings', icon='TIME')
            else:
                row = layout.row()
                row.label(
                    "Enable Show Debug Options to access these settings (only for developers).")

                row = layout.row()
                if preferences.use_custom_icons:
                    row.prop(preferences, 'show_debug_options',
                             icon_value=cicon('code'))
                else:
                    row.prop(preferences, 'show_debug_options',
                             icon='RECOVER_AUTO')

        box = layout.box()
        row = box.row(align=True)
        row.scale_y = 1.2
        if preferences.use_custom_icons:
            row.operator("wm.url_open", text="Our Website", icon_value=cicon(
                'house')).url = "http://crowdmaster.org/"
            row.operator("wm.url_open", text="Email Us", icon_value=cicon(
                'email')).url = "mailto:crowdmaster@jmroper.com"
        else:
            row.operator("wm.url_open", text="Our Website",
                         icon='URL').url = "http://crowdmaster.org/"
            row.operator("wm.url_open", text="Email Us",
                         icon='URL').url = "mailto:crowdmaster@jmroper.com"

        row = box.row()
        row.scale_y = 1.25
        row.operator("scene.cm_save_prefs", icon='SAVE_PREFS')


def draw_cmweb_item(self, context):
    preferences = context.user_preferences.addons[__package__].preferences
    self.layout.separator()
    if preferences.use_custom_icons:
        self.layout.operator("wm.url_open", text="CrowdMaster Website", icon_value=cicon(
            'house'),).url = "http://crowdmaster.org/"
        self.layout.operator("wm.url_open", text="CrowdMaster Email", icon_value=cicon(
            'email'),).url = "mailto:crowdmaster@jmroper.com"
    else:
        self.layout.operator("wm.url_open", text="Our Website",
                             icon='URL').url = "http://crowdmaster.org/"
        self.layout.operator("wm.url_open", text="Email Us",
                             icon='URL').url = "mailto:crowdmaster@jmroper.com"


def register():
    bpy.utils.register_class(CMSavePrefs)
    bpy.utils.register_class(CMPreferences)
    bpy.types.INFO_MT_help.append(draw_cmweb_item)


def unregister():
    bpy.utils.unregister_class(CMSavePrefs)
    bpy.utils.unregister_class(CMPreferences)
    bpy.types.INFO_MT_help.remove(draw_cmweb_item)
