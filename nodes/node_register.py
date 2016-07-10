import bpy
from . import node_tree
from .sockets.custom import MyCustomSocket
from . import custom

def register_nodes():
    print("Registered nodes!")

def unregister_nodes():
    print("Unregistered nodes!")
    