import os
import bpy

ICONS = 'minus_green minus_red node_tree_logo plus_green plus_yellow start_sim stop_sim agents reset instant_setup add_agents plug code shuffle'.split(' ')
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

def cicon(name):
    pcoll = icon_collection["main"]
    return pcoll[name].icon_id
