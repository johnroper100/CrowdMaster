import os
import bpy

ICONS = '3_agents 2_agents 1_agent'.split(' ')
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