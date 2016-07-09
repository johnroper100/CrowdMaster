import os
import bpy

icons_collection = None
icons_directory = os.path.dirname(__file__)

def get_icon_id(identifier):
    # The initialize_icons_collection function needs to be called first.
    return get_icon(identifier).icon_id

def get_icon(identifier):
    if identifier in icons_collection:
        return icons_collection[identifier]
    return icons_collection.load(identifier, os.path.join(icons_directory, identifier + ".png"), "IMAGE")

def initialize_icons_collection():
    global icons_collection
    icons_collection = bpy.utils.previews.new()

def unload_icons():
    bpy.utils.previews.remove(icons_collection)

class IconsMock:
    def get(self, identifier):
        return get_icon(identifier)

icons = IconsMock()
