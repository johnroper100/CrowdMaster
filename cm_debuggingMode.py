import bpy
from . import cm_prefs

preferences = context.user_preferences.addons[__package__].preferences
debugMode = preferences.show_debug_options
