import os
import bpy
import bpy.utils.previews

# global variable to store icons in
cm_custom_icons = None

def register():
    global cm_custom_icons
    cm_custom_icons = bpy.utils.previews.new()
    script_path = bpy.context.space_data.text.filepath
    icons_dir = os.path.join(os.path.dirname(script_path), "icons")
    cm_custom_icons.load("3_agents", os.path.join(icons_dir, "3_agents.png"), 'IMAGE')
    cm_custom_icons.load("2_agents", os.path.join(icons_dir, "2_agents.png"), 'IMAGE')
    cm_custom_icons.load("1_agent", os.path.join(icons_dir, "1_agent.png"), 'IMAGE')
    bpy.utils.register_module(__name__)

def unregister():
    global cm_custom_icons
    bpy.utils.previews.remove(cm_custom_icons)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()