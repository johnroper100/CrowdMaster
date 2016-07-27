import bpy
from . import cm_prefs

preferences = context.user_preferences.addons[__package__].preferences
if preferences.show_debug_options == True:
    debugMode = True
else:
    debugMode = False
