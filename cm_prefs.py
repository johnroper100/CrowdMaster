import bpy
import os
from bpy.types import AddonPreferences
from bpy.props import *
from . import addon_updater_ops
from . import icon_load
from . icon_load import cicon

class CMSavePrefs(bpy.types.Operator):
    """Save the CrowdMaster preferences """
    bl_idname = "scene.cm_save_prefs"
    bl_label = "Save Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.wm.save_userpref()

        return {'FINISHED'}

class CMPreferences(AddonPreferences):
    # bl_idname = "CrowdMaster"
    bl_idname = __package__
    scriptdir = bpy.path.abspath(os.path.dirname(__file__))
    
    auto_check_update = BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = False,
        )
    
    updater_intrval_months = IntProperty(
        name='Months',
        description = "Number of months between checking for updates",
        default=0,
        min=0
        )
    updater_intrval_days = IntProperty(
        name='Days',
        description = "Number of days between checking for updates",
        default=14,
        min=0,
        )
    updater_intrval_hours = IntProperty(
        name='Hours',
        description = "Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
        )
    updater_intrval_minutes = IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
        )
    
    use_custom_icons = BoolProperty(
        name = "Use Custom Icons",
        description = "Chose whether to use the custom icons that come with the addon or not.",
        default = True,
        )
    
    show_debug_options = BoolProperty(
        name = "Show Debug Options",
        description = "Chose whether to show the debug options in the interface. This also enables debug mode.",
        default = True,
        )
    
    play_animation = BoolProperty(
        name = "Start Animation Automatically",
        description = "Start and stop the animation automatically when the start and stop sim buttons are pressed.",
        default = True,
        )
    
    prefs_tab_items = [
        ("GEN", "General Settings", "General settings for the addon."),
        ("UPDATE", "Addon Update Settings", "Settings for the addon updater.") ]

    prefs_tab = EnumProperty(name="Options Set", items=prefs_tab_items)

    def draw(self, context):
        layout = self.layout
        preferences = context.user_preferences.addons[__package__].preferences

        row = layout.row()
        row.prop(preferences, "prefs_tab", expand = True)
        
        if preferences.prefs_tab == "GEN":
            row = layout.row()
            row.prop(preferences, 'use_custom_icons', icon_value=cicon('plug'))
            if preferences.use_custom_icons == True:
                row.prop(preferences, 'show_debug_options', icon_value=cicon('code'))
            else:
                row.prop(preferences, 'show_debug_options', icon='RECOVER_AUTO')
                
            row = layout.row()
            if preferences.use_custom_icons == True:
                row.prop(preferences, 'play_animation', icon_value=cicon('shuffle'))
            else:
                row.prop(preferences, 'play_animation', icon='ACTION')

        if preferences.prefs_tab == "UPDATE":
            row = layout.row()
            addon_updater_ops.update_settings_ui(self,context)
        
        row = layout.row()
        row.scale_y = 1.25
        row.operator("scene.cm_save_prefs", icon='SAVE_PREFS')
