import bpy
from bpy.types import NodeTree, Node, NodeSocket

# Implementation of custom nodes from Python


# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class CMNodeTree(NodeTree):
    '''The CrowdMaster node tree'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'CMNodeTree'
    # Label for nice name display
    bl_label = 'CrowdMaster'
    # Icon identifier
    bl_icon = 'NODETREE'

def register():
    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)

def unregister():
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")

if __name__ == "__main__":
    register()
