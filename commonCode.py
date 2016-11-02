"""Here is some common code that is used throughout CrowdMaster. It is placed here to make my life easier when trying to find things."""

# Standard preferences definition
preferences = context.user_preferences.addons[__package__].preferences

# Preferences definition when not inheriting CONTEXT
preferences = bpy.context.user_preferences.addons[__package__].preferences

# Preferences definition when module gives errors with __package__
preferences = context.user_preferences.addons["CrowdMaster"].preferences
