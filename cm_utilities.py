import bpy
import os
from bpy.props import FloatProperty, StringProperty, BoolProperty
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty

def register():
    print("CrowdMaster sys hi!")

def unregister():
    print("CrowdMaster sys bye!")

if __name__ == "__main__":
    register()
