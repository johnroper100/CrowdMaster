import bpy
import os
from bpy.types import AddonPreferences
from bpy.props import *
from . import addon_updater_ops
from . import icon_load

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

    databaseName = StringProperty \
      (
      name = "Database Name",
      default = "crowdmaster",
      description = "Choose the name of the database",
      )
    
    databaseHost = StringProperty \
      (
      name = "Database Host",
      default = "localhost",
      description = "Choose the database host",
      )
    
    databaseUsername = StringProperty \
      (
      name = "Username",
      default = "",
      description = "Choose your mysql username"
      )
    
    databasePassword = StringProperty \
      (
      name = "Password",
      default = "",
      description = "Choose your mysql password",
      subtype='PASSWORD'
      )
    
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
    
    prefs_tab_items = [
        ("MYSQL", "MySQL Settings", "MySQL general settings"),
        ("DBSETUP", "Database Setup", "MySQL database setup"),
        ("UPDATE", "Addon Update Settings", "Settings for the addon updater") ]

    prefs_tab = EnumProperty(name="Options Set", items=prefs_tab_items)

    def draw(self, context):
        layout = self.layout
        preferences = context.user_preferences.addons[__package__].preferences
        
        pcoll = icon_load.icon_collection["main"]
        def cicon(name):
            return pcoll[name].icon_id

        row = layout.row()
        row.prop(preferences, "prefs_tab", expand = True)
        
        if preferences.prefs_tab == "MYSQL":
            row = layout.row()
            row.prop(preferences, 'databaseName')

            row = layout.row()
            row.prop(preferences, 'databaseHost')

            row = layout.row()
            row.prop(preferences, 'databaseUsername')

            row = layout.row()
            row.prop(preferences, 'databasePassword')
        
        if preferences.prefs_tab == "DBSETUP":
            row = layout.row()
            if (preferences.databaseName == "") or (preferences.databaseHost == "") or (preferences.databaseUsername == "") or (preferences.databasePassword == ""):
                row.enabled = False
            row.operator("scene.cm_init_database", icon_value=cicon('setup_plug'))
        
        if preferences.prefs_tab == "UPDATE":
            row = layout.row()
            addon_updater_ops.update_settings_ui(self,context)
        
        row = layout.row()
        row.scale_y = 1.25
        if (preferences.databaseName == "") or (preferences.databaseHost == "") or (preferences.databaseUsername == "") or (preferences.databasePassword == ""):
            row.enabled = False
        row.operator("scene.cm_save_prefs", icon='SAVE_PREFS')
