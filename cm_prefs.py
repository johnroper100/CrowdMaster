import bpy
import os

class CMSavePrefs(bpy.types.Operator):
    """Save the CrowdMaster preferences """
    bl_idname = "scene.cm_save_prefs"
    bl_label = "Save Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.wm.save_userpref()

        return {'FINISHED'}

class CMPreferences(bpy.types.AddonPreferences):
    # bl_idname = "CrowdMaster"
    bl_idname = __package__
    scriptdir = bpy.path.abspath(os.path.dirname(__file__))

    databaseName = bpy.props.StringProperty \
      (
      name = "Database Name",
      default = "crowdmaster",
      description = "Choose the name of the database",
      )
    
    databaseHost = bpy.props.StringProperty \
      (
      name = "Database Host",
      default = "localhost",
      description = "Choose the database host",
      )
    
    databaseUsername = bpy.props.StringProperty \
      (
      name = "Username",
      default = "",
      description = "Choose your mysql username"
      )
    
    databasePassword = bpy.props.StringProperty \
      (
      name = "Password",
      default = "",
      description = "Choose your mysql password",
      subtype='PASSWORD'
      )

    def draw(self, context):
        layout = self.layout
        preferences = context.user_preferences.addons[__package__].preferences

        row = layout.row()
        row.prop(preferences, 'databaseName')
        
        row = layout.row()
        row.prop(preferences, 'databaseHost')
        
        row = layout.row()
        row.prop(preferences, 'databaseUsername')
        
        row = layout.row()
        row.prop(preferences, 'databasePassword')
        
        row = layout.row()
        row.scale_y = 1.25
        if (preferences.databaseName == "") or (preferences.databaseHost == "") or (preferences.databaseUsername == "") or (preferences.databasePassword == ""):
            row.enabled = False
        row.operator("scene.cm_save_prefs", icon='SAVE_PREFS')